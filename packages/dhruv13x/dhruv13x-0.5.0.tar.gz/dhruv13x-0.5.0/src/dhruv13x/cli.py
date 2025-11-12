import typer

app = typer.Typer(help="Dhruv13x full developer toolkit.")

@app.command()
def tools():
    """List all installed tools."""
    print("""
✅ Installed meta tools:

- duplifinder
- create-dump
- autoheader
- enterprise-docs
- pyinitgen
- pypurge
- import-surgeon
- projectclone
- projectrestore
- importdoc
- routine-workflow
""")

@app.command()
def version():
    """Show meta-suite version."""
    from .version import __version__
    print(f"dhruv13x meta-suite version: {__version__}")