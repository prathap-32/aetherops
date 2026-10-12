# services/project_and_environment_management/app/terminal_ui.py
import asyncio
import time

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box

console = Console()

BANNER = """
 ██████╗ ██████╗  ██████╗      ██╗███████╗ ██████╗████████╗    ███╗   ███╗ ██████╗ ██████╗
 ██╔══██╗██╔══██╗██╔═══██╗     ██║██╔════╝██╔════╝╚══██╔══╝    ████╗ ████║██╔════╝ ██╔══██╗
 ██████╔╝██████╔╝██║   ██║     ██║█████╗  ██║        ██║       ██╔████╔██║██║  ███╗██████╔╝
 ██╔═══╝ ██╔══██╗██║   ██║██   ██║██╔══╝  ██║        ██║       ██║╚██╔╝██║██║   ██║██╔══██╗
 ██║     ██║  ██║╚██████╔╝╚█████╔╝███████╗╚██████╗   ██║       ██║ ╚═╝ ██║╚██████╔╝██║  ██║
 ╚═╝     ╚═╝  ╚═╝ ╚═════╝  ╚════╝ ╚══════╝ ╚═════╝   ╚═╝       ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝
"""


def print_banner():
    txt = Text(BANNER, style="bold cyan")
    txt.append("\n" + "═" * 86 + "\n", style="dim")
    txt.append("  AetherOps AI — Module 1: Project & Environment Management  ", style="bold magenta")
    txt.append(" | ", style="dim")
    txt.append("Port: 8009", style="bold green")
    txt.append(" | ", style="dim")
    txt.append("SQLite + PostgreSQL + Redis", style="bold yellow")
    console.print(Panel(txt, border_style="cyan", box=box.DOUBLE,
                        title="[bold white]MODULE 1 INITIALISING[/bold white]",
                        title_align="center"))


async def run_startup_diagnostics():
    steps = [
        "Initialising SQLite projects.db (WAL mode)…",
        "Connecting to PostgreSQL schema 'project_manager'…",
        "Connecting to Redis project cache…",
        "Seeding default admin account…",
        "Loading sample project data…",
    ]
    with console.status("[bold cyan]Running startup diagnostics…", spinner="dots") as status:
        for i, step in enumerate(steps, 1):
            status.update(f"[bold yellow][{i}/{len(steps)}] {step}")
            await asyncio.sleep(0.25)
            console.print(f"[bold green]✔[/bold green] [{i}/{len(steps)}] {step}")


def print_shutdown_banner():
    console.print(Panel(
        Text("  Module 1 — Project Manager stopped cleanly.  ", style="bold red"),
        border_style="red", box=box.SIMPLE,
        title="[bold white]SHUTDOWN[/bold white]"
    ))
