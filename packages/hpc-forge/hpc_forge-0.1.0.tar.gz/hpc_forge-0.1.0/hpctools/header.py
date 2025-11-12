from datetime import datetime
from rich.console import Console
from rich.panel import Panel

def print_header(app_name="HPC Tools", version="0.1.0"):
    console = Console()
    banner = r"""
██╗  ██╗██████╗  ██████╗████████╗ ████████╗ ██████╗  ██████╗ ██╗     ███████╗
██║  ██║██╔══██╗██╔════╝╚══██╔══╝ ╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██╔════╝
███████║██████╔╝██║        ██║        ██║   ██║   ██║██║   ██║██║     ███████╗
██╔══██║██╔══██╗██║        ██║        ██║   ██║   ██║██║   ██║██║     ╚════██║
██║  ██║██║  ██║╚██████╗   ██║        ██║   ╚██████╔╝╚██████╔╝███████╗███████║
╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝   ╚═╝        ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚══════╝
                  Automate • Build • Run • Analyze ⚙️
"""
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    console.print(Panel.fit(
        f"[bold cyan]{banner}[/bold cyan]\n"
        f"[yellow]{app_name}[/yellow] [dim]{version}[/dim] — {time_str}\n"
        f"[green]Ready to forge your HPC environment[/green]",
        border_style="bright_blue",
    ))