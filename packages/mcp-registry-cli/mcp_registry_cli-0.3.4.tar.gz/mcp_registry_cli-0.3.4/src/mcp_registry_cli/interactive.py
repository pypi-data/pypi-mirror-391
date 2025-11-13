"""Interactive CLI interface for MCP Registry."""

import os
import sys
from typing import List, Optional, Dict, Any
import time

# Check for required dependencies
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.layout import Layout
    from rich.live import Live
    from rich.prompt import Prompt, Confirm
    from rich.progress import track
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from .api import MCPRegistryAPI, Server


class InteractiveCLI:
    """Interactive CLI for navigating MCP Registry."""
    
    def __init__(self):
        self.console = Console()
        self.api = MCPRegistryAPI()
        self.current_servers: List[Server] = []
        self.all_servers: List[Server] = []  # Unfiltered list for live search
        self.selected_index = 0
        self.search_query = ""
        self.live_filter = ""  # Real-time filter text
        self.status_filter = ""
        self.current_cursor = None
        self.page_cursors = []  # Stack of cursors for previous pages
        self.has_next_page = False
        self.page_size = 30
        self.current_page = 1
        self.running = True
        self.search_mode = False  # Flag for live search mode
        
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('clear' if os.name == 'posix' else 'cls')
        
    def create_header(self) -> Panel:
        """Create the header panel."""
        title_text = Text()
        title_text.append("🚀 MCP Registry Interactive CLI", style="bold cyan")

        status_text = Text()
        page_info = f"Page {self.current_page}"
        if self.has_next_page:
            page_info += "+ | "  # Indicates more pages available
        else:
            page_info += " | "  # This is likely the last page
        status_text.append(f"{page_info}Servers: {len(self.current_servers)} | ", style="dim")
        if self.search_query:
            status_text.append(f"Search: '{self.search_query}' | ", style="yellow")
        if self.live_filter:
            status_text.append(f"Filter: '{self.live_filter}' | ", style="cyan")
        if self.status_filter:
            status_text.append(f"Status: {self.status_filter} | ", style="green")
        status_text.append("← → Pages | ↑ ↓ Navigate | '/' to filter | 'h' for help", style="dim")

        header_content = Text()
        header_content.append(title_text)
        header_content.append("\n")
        header_content.append(status_text)

        return Panel(header_content, title="MCP Registry", border_style="blue")
    
    def create_server_table(self) -> Table:
        """Create the server list table."""
        table = Table(show_header=True, header_style="bold magenta", box=None)
        table.add_column("", width=3)  # Selection indicator
        table.add_column("Name", style="cyan", no_wrap=False, min_width=30)
        table.add_column("Status", justify="center", width=10)
        table.add_column("Version", justify="center", width=8)
        table.add_column("Description", style="dim", no_wrap=False)
        
        for i, server in enumerate(self.current_servers):
            # Selection indicator
            indicator = "▶" if i == self.selected_index else " "
            
            # Status styling
            status_style = {
                "active": "green",
                "inactive": "red", 
                "deprecated": "yellow"
            }.get(server.status.lower(), "white")
            
            # Truncate description
            desc = server.description
            if len(desc) > 60:
                desc = desc[:57] + "..."
            
            # Highlight selected row
            if i == self.selected_index:
                table.add_row(
                    f"[bold yellow]{indicator}[/bold yellow]",
                    f"[bold white]{server.name}[/bold white]",
                    f"[bold {status_style}]{server.status}[/bold {status_style}]",
                    f"[bold white]{server.version or 'N/A'}[/bold white]",
                    f"[bold white]{desc}[/bold white]"
                )
            else:
                table.add_row(
                    indicator,
                    server.name,
                    f"[{status_style}]{server.status}[/{status_style}]",
                    server.version or "N/A",
                    desc
                )
        
        return table
    
    def create_help_panel(self) -> Panel:
        """Create the help panel."""
        help_text = Text()
        help_text.append("Navigation:\n", style="bold")
        help_text.append("↑/↓ or k/j   - Navigate servers\n")
        help_text.append("←/→ or p/n   - Previous/Next page\n", style="cyan")
        help_text.append("Enter        - View server details\n")
        help_text.append("i            - Install selected server\n")
        help_text.append("/            - Live filter (type to filter current page)\n", style="yellow")
        help_text.append("Esc          - Exit live filter mode\n")
        help_text.append("s            - Search servers (API search)\n")
        help_text.append("f            - Filter by status\n")
        help_text.append("x            - Show registry statistics\n", style="magenta")
        help_text.append("c            - Clear filters\n")
        help_text.append("r            - Refresh server list\n")
        help_text.append("h            - Show/hide help\n")
        help_text.append("q            - Quit\n")

        return Panel(help_text, title="Help", border_style="green")
    
    def create_layout(self, show_help: bool = False) -> Layout:
        """Create the main layout."""
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=4),
            Layout(name="main")
        )
        
        layout["header"].update(self.create_header())
        
        if show_help:
            layout["main"].split_row(
                Layout(name="servers", ratio=2),
                Layout(name="help", ratio=1)
            )
            layout["servers"].update(self.create_server_table())
            layout["help"].update(self.create_help_panel())
        else:
            layout["main"].update(self.create_server_table())
        
        return layout
    
    def load_servers(self, search: str = "", status: str = "", cursor: str = None, reset_pagination: bool = True):
        """Load servers from API."""
        try:
            if search:
                result = self.api.search_servers(search, cursor=cursor, limit=self.page_size)
            else:
                result = self.api.list_servers(cursor=cursor, limit=self.page_size)

            servers = result["servers"]

            # Filter to show only latest version of each server
            seen_servers = {}
            filtered_servers = []
            for server in servers:
                # Check if this is the latest version
                is_latest = False
                if server.meta and "io.modelcontextprotocol.registry/official" in server.meta:
                    is_latest = server.meta["io.modelcontextprotocol.registry/official"].get("isLatest", False)

                # Only include if it's the latest version or if we haven't seen this server yet
                if is_latest or server.name not in seen_servers:
                    if server.name not in seen_servers or is_latest:
                        seen_servers[server.name] = server
                        if is_latest:
                            # Replace with latest version if we already added a non-latest one
                            filtered_servers = [s for s in filtered_servers if s.name != server.name]
                            filtered_servers.append(server)
                        else:
                            filtered_servers.append(server)

            servers = filtered_servers

            # Apply status filter if set
            if status:
                servers = [s for s in servers if s.status.lower() == status.lower()]

            # Store both full list and filtered list
            self.all_servers = servers
            self.apply_live_filter()

            self.current_cursor = result.get("next_cursor")
            self.has_next_page = bool(self.current_cursor)
            self.selected_index = 0

            if reset_pagination:
                self.current_page = 1
                self.page_cursors = []

        except Exception as e:
            self.console.print(f"[red]Error loading servers: {e}[/red]")
            self.current_servers = []
            self.all_servers = []

    def apply_live_filter(self):
        """Apply live filter to current servers list."""
        if not self.live_filter:
            self.current_servers = self.all_servers
        else:
            filter_lower = self.live_filter.lower()
            self.current_servers = [
                s for s in self.all_servers
                if filter_lower in s.name.lower() or filter_lower in s.description.lower()
            ]
    
    def show_server_details(self, server: Server):
        """Show detailed server information."""
        self.clear_screen()

        # Main info panel
        info_text = Text()
        info_text.append(f"Name: {server.name}\n", style="bold cyan")
        info_text.append(f"Status: ", style="bold")

        status_style = {
            "active": "green",
            "inactive": "red",
            "deprecated": "yellow"
        }.get(server.status.lower(), "white")
        info_text.append(f"{server.status}\n", style=status_style)

        if server.version:
            info_text.append(f"Version: {server.version}\n", style="bold")

        info_text.append(f"\nDescription:\n{server.description}", style="white")

        self.console.print(Panel(info_text, title="Server Information", border_style="blue"))

        # Repository info
        if server.repository:
            repo_text = Text()
            repo_text.append(f"Type: {server.repository.get('url', 'N/A')}\n", style="cyan")
            repo_text.append(f"URL: {server.repository.get('url', 'N/A')}\n", style="cyan")
            if server.repository.get('ref'):
                repo_text.append(f"Ref: {server.repository.get('ref')}\n", style="cyan")

            self.console.print(Panel(repo_text, title="Repository", border_style="green"))

        # Fetch and display all available versions
        try:
            self.console.print("[dim]Fetching available versions...[/dim]")
            all_versions = self.api.get_server_versions(server.name)

            if all_versions and len(all_versions) > 1:
                versions_table = Table(show_header=True, header_style="bold magenta")
                versions_table.add_column("#", style="cyan", width=5)
                versions_table.add_column("Version", style="yellow")
                versions_table.add_column("Status", style="green", justify="center")
                versions_table.add_column("Published", style="dim")
                versions_table.add_column("Latest", style="cyan", justify="center")

                for idx, ver in enumerate(all_versions, 1):
                    is_latest = ver.meta.get("io.modelcontextprotocol.registry/official", {}).get("isLatest", False) if ver.meta else False
                    published = ver.meta.get("io.modelcontextprotocol.registry/official", {}).get("publishedAt", "N/A") if ver.meta else "N/A"
                    if published != "N/A":
                        # Format date to be more readable
                        try:
                            from datetime import datetime
                            dt = datetime.fromisoformat(published.replace('Z', '+00:00'))
                            published = dt.strftime("%Y-%m-%d %H:%M")
                        except:
                            pass

                    versions_table.add_row(
                        str(idx),
                        ver.version or "N/A",
                        ver.status,
                        published,
                        "✓" if is_latest else ""
                    )

                self.console.print(Panel(versions_table, title=f"Available Versions ({len(all_versions)})", border_style="cyan"))
        except Exception as e:
            self.console.print(f"[yellow]Could not fetch versions: {e}[/yellow]")

        # Packages info
        if server.packages:
            packages_table = Table(show_header=True, header_style="bold magenta")
            packages_table.add_column("Registry", style="cyan")
            packages_table.add_column("Package", style="yellow")
            packages_table.add_column("Version", style="green")

            for package in server.packages:
                packages_table.add_row(
                    package.get("registry", "N/A"),
                    package.get("package", "N/A"),
                    package.get("version", "N/A")
                )

            self.console.print(Panel(packages_table, title="Installation Packages", border_style="cyan"))

        # Controls
        self.console.print("\n[dim]Options: [bold]i[/bold] = Install | [bold]v[/bold] = Install specific version | [bold]any other key[/bold] = Return[/dim]")

        # Wait for key press
        try:
            key = input().lower().strip()
            if key == 'i':
                self.install_server(server)
            elif key == 'v':
                self.install_server_version(server)
        except KeyboardInterrupt:
            pass
    
    def live_search_mode(self):
        """Enter live search mode where user can type to filter current page."""
        import sys
        import tty
        import termios

        # Store original terminal settings
        try:
            fd = sys.stdin.fileno()
            if not os.isatty(fd):
                # Fallback for non-tty environments
                self.search_servers()
                return

            old_settings = termios.tcgetattr(fd)
        except:
            # Fallback if terminal control is not available
            self.search_servers()
            return

        self.live_filter = ""
        searching = True

        try:
            while searching:
                # Redraw screen with current filter
                self.clear_screen()
                self.apply_live_filter()
                if self.selected_index >= len(self.current_servers):
                    self.selected_index = max(0, len(self.current_servers) - 1)

                layout = self.create_layout(False)
                self.console.print(layout)

                # Show search input line
                self.console.print(f"\n[bold cyan]Live Filter:[/bold cyan] {self.live_filter}_ [dim](Esc to exit, Backspace to delete)[/dim]")

                # Get character input
                tty.setraw(fd, termios.TCSANOW)
                try:
                    ch = sys.stdin.read(1)

                    # Handle special keys
                    if ch == '\x1b':  # ESC or arrow key
                        # Check if it's an escape sequence
                        ch2 = sys.stdin.read(1)
                        if ch2 == '[':
                            ch3 = sys.stdin.read(1)
                            # Ignore arrow keys in search mode
                            continue
                        else:
                            # ESC key pressed - exit search mode
                            searching = False
                            break
                    elif ch == '\x7f' or ch == '\x08':  # Backspace or Delete
                        if len(self.live_filter) > 0:
                            self.live_filter = self.live_filter[:-1]
                    elif ch == '\r' or ch == '\n':  # Enter
                        # Exit search mode and keep the filter
                        searching = False
                    elif ord(ch) == 3:  # Ctrl+C
                        raise KeyboardInterrupt
                    elif ch.isprintable():
                        # Add character to filter
                        self.live_filter += ch
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

                time.sleep(0.05)  # Small delay to prevent excessive CPU usage

        except KeyboardInterrupt:
            self.live_filter = ""
            self.apply_live_filter()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def show_registry_stats(self):
        """Display registry statistics."""
        self.clear_screen()

        self.console.print("[bold cyan]📊 Gathering Registry Statistics...[/bold cyan]\n")
        self.console.print("[dim]This may take a moment as we fetch data from the registry...[/dim]\n")

        try:
            # Fetch multiple pages to get comprehensive stats
            all_servers = []
            cursor = None
            max_pages = 10  # Fetch up to 10 pages (300 servers)

            for page in range(max_pages):
                result = self.api.list_servers(cursor=cursor, limit=30)
                all_servers.extend(result['servers'])
                cursor = result.get('next_cursor')
                self.console.print(f"[dim]Fetched page {page + 1}... ({len(all_servers)} servers)[/dim]")
                if not cursor:
                    break

            self.clear_screen()

            # Calculate statistics
            unique_servers = {}
            version_counts = {}
            status_counts = {}
            sources = {}
            with_packages = 0
            with_remotes = 0

            for server in all_servers:
                # Count unique servers
                if server.name not in unique_servers:
                    unique_servers[server.name] = []
                unique_servers[server.name].append(server)

                # Count versions
                if server.version:
                    version_counts[server.version] = version_counts.get(server.version, 0) + 1

                # Count by status
                status_counts[server.status] = status_counts.get(server.status, 0) + 1

                # Count sources
                if server.repository and server.repository.get('source'):
                    source = server.repository['source']
                    sources[source] = sources.get(source, 0) + 1

                # Count packages and remotes
                if server.packages:
                    with_packages += 1
                if server.remotes:
                    with_remotes += 1

            # Display stats
            title = Text()
            title.append("📊 MCP Registry Statistics", style="bold cyan")

            # Overview stats
            overview = Text()
            overview.append(f"Total Server Entries: ", style="bold white")
            overview.append(f"{len(all_servers)}\n", style="bold green")
            overview.append(f"Unique Servers: ", style="bold white")
            overview.append(f"{len(unique_servers)}\n", style="bold green")
            overview.append(f"Average Versions per Server: ", style="bold white")
            avg_versions = len(all_servers) / len(unique_servers) if unique_servers else 0
            overview.append(f"{avg_versions:.2f}\n", style="bold green")

            self.console.print(Panel(overview, title="Overview", border_style="cyan"))

            # Status breakdown
            status_table = Table(show_header=True, header_style="bold magenta")
            status_table.add_column("Status", style="cyan")
            status_table.add_column("Count", justify="right", style="green")
            status_table.add_column("Percentage", justify="right", style="yellow")

            for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / len(all_servers) * 100) if all_servers else 0
                status_table.add_row(status, str(count), f"{percentage:.1f}%")

            self.console.print(Panel(status_table, title="Status Distribution", border_style="green"))

            # Deployment info
            deploy_table = Table(show_header=True, header_style="bold magenta")
            deploy_table.add_column("Type", style="cyan")
            deploy_table.add_column("Count", justify="right", style="green")
            deploy_table.add_column("Percentage", justify="right", style="yellow")

            pkg_pct = (with_packages / len(all_servers) * 100) if all_servers else 0
            rem_pct = (with_remotes / len(all_servers) * 100) if all_servers else 0
            deploy_table.add_row("With Packages", str(with_packages), f"{pkg_pct:.1f}%")
            deploy_table.add_row("With Remotes", str(with_remotes), f"{rem_pct:.1f}%")

            self.console.print(Panel(deploy_table, title="Deployment Methods", border_style="blue"))

            # Repository sources
            if sources:
                sources_table = Table(show_header=True, header_style="bold magenta")
                sources_table.add_column("Source", style="cyan")
                sources_table.add_column("Count", justify="right", style="green")

                for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
                    sources_table.add_row(source or "unknown", str(count))

                self.console.print(Panel(sources_table, title="Repository Sources", border_style="yellow"))

            # Version distribution (top 5)
            if version_counts:
                version_table = Table(show_header=True, header_style="bold magenta")
                version_table.add_column("Version", style="cyan")
                version_table.add_column("Count", justify="right", style="green")

                top_versions = sorted(version_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                for version, count in top_versions:
                    version_table.add_row(version, str(count))

                self.console.print(Panel(version_table, title="Top 5 Version Numbers", border_style="magenta"))

            self.console.print(f"\n[dim]Statistics based on {len(all_servers)} server entries (up to {max_pages} pages)[/dim]")

        except Exception as e:
            self.console.print(f"[red]Error gathering statistics: {e}[/red]")

        self.console.print("\n[dim]Press any key to return...[/dim]")
        try:
            input()
        except KeyboardInterrupt:
            pass

    def search_servers(self):
        """Interactive search."""
        query = Prompt.ask("🔍 Enter search term", default=self.search_query)
        if query != self.search_query:
            self.search_query = query
            self.load_servers(search=self.search_query, status=self.status_filter)
    
    def filter_by_status(self):
        """Interactive status filter."""
        status = Prompt.ask(
            "📊 Filter by status",
            choices=["active", "inactive", "deprecated", "clear", ""],
            default=self.status_filter or "active"
        )
        
        if status == "clear" or status == "":
            self.status_filter = ""
        else:
            self.status_filter = status
            
        self.load_servers(search=self.search_query, status=self.status_filter)
    
    def next_page(self):
        """Load next page of servers."""
        if not self.has_next_page:
            return
        
        # Store current cursor for going back
        self.page_cursors.append(self.current_cursor)
        self.current_page += 1
        
        self.load_servers(
            search=self.search_query,
            status=self.status_filter,
            cursor=self.current_cursor,
            reset_pagination=False
        )
    
    def previous_page(self):
        """Load previous page of servers."""
        if self.current_page <= 1:
            return
        
        self.current_page -= 1
        
        if self.current_page == 1:
            # Go back to first page
            cursor = None
        else:
            # Use stored cursor for previous page
            cursor = self.page_cursors[-2] if len(self.page_cursors) > 1 else None
        
        # Remove the last cursor
        if self.page_cursors:
            self.page_cursors.pop()
        
        self.load_servers(
            search=self.search_query,
            status=self.status_filter,
            cursor=cursor,
            reset_pagination=False
        )
    
    def install_server(self, server: Server):
        """Interactive server installation."""
        if not server.packages:
            self.console.print(f"[red]No installation packages available for {server.name}[/red]")
            input("Press any key to continue...")
            return

        self.console.print(f"[cyan]Installing {server.name}...[/cyan]")

        # Show available packages
        packages_table = Table(show_header=True, header_style="bold magenta")
        packages_table.add_column("Option", style="cyan")
        packages_table.add_column("Registry", style="yellow")
        packages_table.add_column("Package", style="green")
        packages_table.add_column("Command", style="dim")

        install_options = []
        for i, package in enumerate(server.packages):
            registry = package.get("registry", "")
            package_name = package.get("package", "")
            version = package.get("version", "")

            if registry == "npm":
                cmd = f"npm install {package_name}"
                if version:
                    cmd += f"@{version}"
            elif registry == "pypi":
                cmd = f"pip install {package_name}"
                if version:
                    cmd += f"=={version}"
            else:
                cmd = f"# Unknown registry: {registry}"

            install_options.append(cmd)
            packages_table.add_row(str(i + 1), registry, package_name, cmd)

        self.console.print(packages_table)

        # Get user choice
        if len(install_options) == 1:
            choice = "1"
        else:
            choice = Prompt.ask(
                f"Choose package to install (1-{len(install_options)})",
                choices=[str(i) for i in range(1, len(install_options) + 1)]
            )

        selected_cmd = install_options[int(choice) - 1]

        # Confirm installation
        if Confirm.ask(f"Execute: [bold]{selected_cmd}[/bold]?"):
            try:
                import subprocess
                self.console.print(f"[cyan]Executing: {selected_cmd}[/cyan]")

                result = subprocess.run(selected_cmd.split(), capture_output=True, text=True)
                if result.returncode == 0:
                    self.console.print(f"[green]✓ Successfully installed {server.name}[/green]")
                else:
                    self.console.print(f"[red]✗ Installation failed: {result.stderr}[/red]")

            except Exception as e:
                self.console.print(f"[red]✗ Installation error: {str(e)}[/red]")

        input("Press any key to continue...")

    def install_server_version(self, server: Server):
        """Install a specific version of a server."""
        try:
            # Fetch all versions
            all_versions = self.api.get_server_versions(server.name)

            if not all_versions:
                self.console.print(f"[red]No versions available for {server.name}[/red]")
                input("Press any key to continue...")
                return

            # Display versions
            versions_table = Table(show_header=True, header_style="bold magenta")
            versions_table.add_column("Option", style="cyan", width=8)
            versions_table.add_column("Version", style="yellow")
            versions_table.add_column("Status", style="green", justify="center")
            versions_table.add_column("Latest", style="cyan", justify="center")

            for idx, ver in enumerate(all_versions, 1):
                is_latest = ver.meta.get("io.modelcontextprotocol.registry/official", {}).get("isLatest", False) if ver.meta else False
                versions_table.add_row(
                    str(idx),
                    ver.version or "N/A",
                    ver.status,
                    "✓" if is_latest else ""
                )

            self.console.print(versions_table)

            # Get version choice
            version_choice = Prompt.ask(
                f"Select version to install (1-{len(all_versions)})",
                choices=[str(i) for i in range(1, len(all_versions) + 1)],
                default="1"
            )

            selected_version = all_versions[int(version_choice) - 1]

            # Check if selected version has packages
            if not selected_version.packages:
                self.console.print(f"[red]No installation packages available for version {selected_version.version}[/red]")
                input("Press any key to continue...")
                return

            # Install the selected version
            self.install_server(selected_version)

        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]")
            input("Press any key to continue...")
    
    def get_key_input(self) -> str:
        """Get single key input (cross-platform) with better fallback."""
        try:
            # Try to import getch for single key input
            if sys.platform == "win32":
                import msvcrt
                key = msvcrt.getch()
                if key == b'\xe0':  # Special key prefix on Windows
                    key = msvcrt.getch()
                    if key == b'H':
                        return 'k'  # Up arrow
                    elif key == b'P':
                        return 'j'  # Down arrow
                    elif key == b'M':
                        return '\x1b[C'  # Right arrow
                    elif key == b'K':
                        return '\x1b[D'  # Left arrow
                return key.decode('utf-8').lower()
            else:
                # Unix/Linux/macOS
                try:
                    import tty, termios
                    fd = sys.stdin.fileno()
                    
                    # Check if stdin is a tty
                    if not os.isatty(fd):
                        return self._smart_input()
                        
                    old_settings = termios.tcgetattr(fd)
                    try:
                        tty.setraw(fd, termios.TCSANOW)  # Use setraw instead of cbreak
                        ch = sys.stdin.read(1)
                        
                        # Handle arrow keys (escape sequences)
                        if ch == '\x1b':  # ESC sequence
                            ch2 = sys.stdin.read(1)
                            if ch2 == '[':
                                ch3 = sys.stdin.read(1)
                                if ch3 == 'A':
                                    return 'k'  # Up arrow
                                elif ch3 == 'B':
                                    return 'j'  # Down arrow
                                elif ch3 == 'C':
                                    return '\x1b[C'  # Right arrow
                                elif ch3 == 'D':
                                    return '\x1b[D'  # Left arrow
                        
                        # Handle Ctrl+C
                        if ord(ch) == 3:
                            raise KeyboardInterrupt
                        
                        return ch.lower()
                    finally:
                        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                except (ImportError, AttributeError, OSError, termios.error):
                    # Fallback for systems without tty support
                    return self._smart_input()
        except Exception:
            return self._smart_input()
    
    def _smart_input(self) -> str:
        """Smart input method that works well without single-key input."""
        self.console.print("\n[cyan]Command:[/cyan] ", end="")
        
        try:
            user_input = input().lower().strip()
            
            # Handle empty input
            if not user_input:
                return 'h'  # Show help if empty
            
            # Handle escape sequences that might come through
            if '^[[A' in user_input or '\x1b[A' in user_input:
                return 'k'  # Up arrow
            elif '^[[B' in user_input or '\x1b[B' in user_input:
                return 'j'  # Down arrow
            
            # Clean up escape sequences
            user_input = user_input.replace('^[[A', '').replace('^[[B', '')
            user_input = user_input.replace('\x1b[A', '').replace('\x1b[B', '')
            user_input = user_input.strip()
            
            # Map full words to single characters
            command_map = {
                'up': 'k', 'k': 'k', 'u': 'k',
                'down': 'j', 'j': 'j', 'd': 'j', 
                'enter': '\n', 'details': '\n', 'view': '\n',
                'install': 'i', 'i': 'i',
                'search': 's', 's': 's', 'find': 's',
                'filter': 'f', 'f': 'f',
                'clear': 'c', 'c': 'c',
                'next': 'n', 'n': 'n', 'more': 'n',
                'prev': 'p', 'p': 'p', 'previous': 'p',
                'left': 'p', 'right': 'n',
                'refresh': 'r', 'r': 'r', 'reload': 'r',
                'help': 'h', 'h': 'h', '?': 'h',
                'quit': 'q', 'q': 'q', 'exit': 'q'
            }
            
            return command_map.get(user_input, user_input if user_input else 'h')
                    
        except (KeyboardInterrupt, EOFError):
            return 'q'
    
    def run(self):
        """Run the interactive CLI."""
        self.console.print("[bold cyan]🚀 Loading MCP Registry...[/bold cyan]")
        
        # Initial load
        self.load_servers()
        
        show_help = False
        
        try:
            while self.running:
                self.clear_screen()
                layout = self.create_layout(show_help)
                self.console.print(layout)
                
                if not self.current_servers:
                    self.console.print("[yellow]No servers found. Press 'r' to refresh or 'q' to quit.[/yellow]")
                
                # Status bar
                status_line = f"[dim]Selected: {self.selected_index + 1}/{len(self.current_servers)} | Page {self.current_page} | "
                if self.current_page > 1:
                    status_line += "← Prev | "
                if self.has_next_page:
                    status_line += "Next → | "
                status_line += "Press 'h' for help[/dim]"
                self.console.print(status_line)
                
                # Get user input
                key = self.get_key_input()
                
                # Handle navigation
                if key in ['k', '\x1b[A']:  # Up arrow or k
                    if self.selected_index > 0:
                        self.selected_index -= 1
                elif key in ['j', '\x1b[B']:  # Down arrow or j  
                    if self.selected_index < len(self.current_servers) - 1:
                        self.selected_index += 1
                elif key in ['\x1b[D', 'p']:  # Left arrow or p (previous page)
                    self.previous_page()
                elif key in ['\x1b[C', 'n']:  # Right arrow or n (next page)
                    if key == 'n' or self.has_next_page:
                        self.next_page()
                elif key in ['\r', '\n']:  # Enter
                    if self.current_servers:
                        server = self.current_servers[self.selected_index]
                        self.show_server_details(server)
                elif key == 'i':  # Install
                    if self.current_servers:
                        server = self.current_servers[self.selected_index]
                        self.install_server(server)
                elif key == 's':  # Search
                    self.search_servers()
                elif key == 'f':  # Filter
                    self.filter_by_status()
                elif key == '/':  # Live filter mode
                    self.live_search_mode()
                elif key == 'x':  # Show statistics
                    self.show_registry_stats()
                elif key == 'c':  # Clear filters
                    self.search_query = ""
                    self.status_filter = ""
                    self.live_filter = ""
                    self.load_servers()
                # Note: 'n' and 'p' are now handled in navigation section above
                elif key == 'r':  # Refresh
                    self.load_servers(search=self.search_query, status=self.status_filter)
                elif key == 'h':  # Help
                    show_help = not show_help
                elif key == 'q':  # Quit
                    self.running = False
                
                # Small delay to prevent flickering
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            pass
        
        self.console.print("\n[cyan]Thanks for using MCP Registry CLI! 👋[/cyan]")


def main():
    """Entry point for interactive CLI."""
    if not RICH_AVAILABLE:
        print("⚠️  Rich library not available. Using simple interactive mode...")
        print("For better experience, install: pip install rich")
        
        # Fall back to simple interactive CLI
        from .interactive_simple import main_simple
        main_simple()
        return
        
    try:
        cli = InteractiveCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()