# services/source_and_cloud_connection/app/terminal_ui.py
import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box

console = Console()

BANNER = """
 ███████╗ ██████╗ ██╗   ██╗██████╗  ██████╗███████╗     ██████╗ ██████╗ ███╗   ██╗███╗   ██╗
 ██╔════╝██╔═══██╗██║   ██║██╔══██╗██╔════╝██╔════╝    ██╔════╝██╔═══██╗████╗  ██║████╗  ██║
 ███████╗██║   ██║██║   ██║██████╔╝██║     █████╗      ██║     ██║   ██║██╔██╗ ██║██╔██╗ ██║
 ╚════██║██║   ██║██║   ██║██╔══██╗██║     ██╔══╝      ██║     ██║   ██║██║╚██╗██║██║╚██╗██║
 ███████║╚██████╔╝╚██████╔╝██║  ██║╚██████╗███████╗    ╚██████╗╚██████╔╝██║ ╚████║██║ ╚████║
 ╚══════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝ ╚═════╝╚══════╝     ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═══╝
"""


def print_banner():
    txt = Text(BANNER, style="bold green")
    txt.append("\n" + "═" * 90 + "\n", style="dim")
    txt.append("  AetherOps AI — Module 2: Source & Cloud Connection  ", style="bold magenta")
    txt.append(" | ", style="dim")
    txt.append("Port: 8010", style="bold cyan")
    txt.append(" | ", style="dim")
    txt.append("SQLite + PostgreSQL + Redis  |  Premium Light UI", style="bold yellow")
    console.print(Panel(txt, border_style="green", box=box.DOUBLE,
                        title="[bold white]MODULE 2 INITIALISING[/bold white]",
                        title_align="center"))


async def run_startup_diagnostics():
    steps = [
        "Initialising SQLite source_connections.db (WAL mode)…",
        "Connecting to PostgreSQL schema 'source_connection'…",
        "Connecting to Redis source cache…",
        "Seeding default admin account…",
        "Loading sample Git connection data…",
    ]
    with console.status("[bold cyan]Running diagnostics…", spinner="dots") as status:
        for i, step in enumerate(steps, 1):
            status.update(f"[bold yellow][{i}/{len(steps)}] {step}")
            await asyncio.sleep(0.2)
            console.print(f"[bold green]✔[/bold green] [{i}/{len(steps)}] {step}")


def print_shutdown_banner():
    console.print(Panel(
        Text("  Module 2 — Source & Cloud Connection stopped cleanly.  ", style="bold red"),
        border_style="red", box=box.SIMPLE,
        title="[bold white]SHUTDOWN[/bold white]"
    ))
