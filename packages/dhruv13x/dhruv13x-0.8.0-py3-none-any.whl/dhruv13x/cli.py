# src/dhruv13x/cli.py

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import print
from pypurge import main as purge_main
from projectclone import cli as clone_cli

console = Console()
app = typer.Typer(help="Dhruv13x — The Unified Developer Toolchain for Modern Python Engineering.")

# === ASCII Banner ===
BANNER = r"""
██████╗ ██╗  ██╗██████╗ ██╗   ██╗██╗   ██╗██╗███╗   ██╗
██╔══██╗██║  ██║██╔══██╗██║   ██║╚██╗ ██╔╝██║████╗  ██║
██████╔╝███████║██████╔╝██║   ██║ ╚████╔╝ ██║██╔██╗ ██║
██╔═══╝ ██╔══██║██╔══██╗██║   ██║  ╚██╔╝  ██║██║╚██╗██║
██║     ██║  ██║██████╔╝╚██████╔╝   ██║   ██║██║ ╚████║
╚═╝     ╚═╝  ╚═╝╚═════╝  ╚═════╝    ╚═╝   ╚═╝╚═╝  ╚═══╝
"""


def banner():
    console.print(Panel.fit(Text(BANNER, style="bold cyan"), border_style="blue", title="dhruv13x"))


@app.callback(invoke_without_command=True)
def main_callback(ctx: typer.Context):
    """Show banner or command help."""
    banner()
    if ctx.invoked_subcommand is None:
        console.print("[bold yellow]Use[/bold yellow] [green]dhruv13x --help[/green] for available commands.\n")


# === CORE COMMANDS ===

@app.command()
def tools():
    """List all installed meta tools."""
    console.print(Panel.fit("""
[bold green]✅ Installed meta tools:[/bold green]

• duplifinder         → detect duplicate definitions
• create-dump         → monorepo code dumper
• autoheader          → header template generator
• enterprise-docs     → doc compliance enforcer
• pyinitgen           → auto __init__.py generator
• pypurge             → clean project clutter
• import-surgeon      → rewrite unsafe imports
• projectclone        → atomic project snapshot
• projectrestore      → restore from snapshot
• importdoc           → import documentation scaffolder
• routine-workflow    → daily developer automation
""", border_style="green", title="Installed Tools"))


@app.command()
def version():
    """Show unified version info."""
    from .version import __version__
    console.print(Panel.fit(f"[bold cyan]dhruv13x meta-suite version:[/bold cyan] [white]{__version__}[/white]",
                            border_style="cyan", title="Version"))


@app.command()
def purge():
    """Run pypurge cleanup tool."""
    console.print("[yellow]Running pypurge cleanup...[/yellow]")
    purge_main()
    console.print("[green]✅ Cleanup complete![/green]")


@app.command()
def clone():
    """Run projectclone CLI."""
    console.print("[yellow]Launching projectclone...[/yellow]")
    clone_cli.main()
    console.print("[green]✅ Clone operation complete.[/green]")


# === FUTURE COMMANDS (add 1 per release) ===
# @app.command()
# def restore(): from projectrestore import cli; cli.main()
# @app.command()
# def dedupe(): from duplifinder import main; main()
# @app.command()
# def import_fix(): from import_surgeon import cli; cli.main()
# @app.command()
# def init(): from pyinitgen import cli; cli.main()
# @app.command()
# def routine(): from routine_workflow import full_routine_workflow; full_routine_workflow.run()
# @app.command()
# def docs(): from enterprise_docs import cli; cli.main()


def run():
    """Entry point for `python -m dhruv13x`."""
    app()


if __name__ == "__main__":
    run()