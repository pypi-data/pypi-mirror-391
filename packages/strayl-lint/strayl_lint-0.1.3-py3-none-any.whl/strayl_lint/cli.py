"""Main CLI application."""

import os
import sys
from pathlib import Path
from typing import Optional, List

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from .scanner import CodeScanner
from .checker import ApiChecker, CheckResult

app = typer.Typer(
    name="strayl-lint",
    help="AI-powered API validation tool - never fear API updates again",
    add_completion=False,
)

console = Console()


@app.command()
def check(
    path: str = typer.Argument(".", help="Path to scan for API calls"),
    api_key: Optional[str] = typer.Option(
        None,
        "--api-key",
        "-k",
        envvar="STRAYL_API_KEY",
        help="Strayl API key (or set STRAYL_API_KEY env var)"
    ),
    extensions: Optional[str] = typer.Option(
        None,
        "--ext",
        "-e",
        help="Comma-separated file extensions to scan (e.g., .py,.js)"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed output"
    ),
):
    """
    Check API calls in your code against their documentation.

    Example:
        strayl-lint check
        strayl-lint check --api-key sk_live_xxx
        strayl-lint check src/ --ext .py,.js
    """
    console.print("\n[bold blue]🐕 Strayl Watchdog[/bold blue] - Checking API calls...\n")

    # Get API key
    if not api_key:
        api_key = ApiChecker.get_api_key()

    if not api_key:
        console.print("[red]❌ Error:[/red] No API key found.")
        console.print("\nGet your API key at: [link]https://strayl.dev/dashboard[/link]")
        console.print("\nThen set it via:")
        console.print("  • Environment variable: export STRAYL_API_KEY=sk_live_xxx")
        console.print("  • Config file: echo 'api_key=sk_live_xxx' > .strayl")
        console.print("  • Command flag: strayl-lint check --api-key sk_live_xxx")
        sys.exit(1)

    # Parse extensions
    ext_list = None
    if extensions:
        ext_list = [ext.strip() for ext in extensions.split(',')]
        if verbose:
            console.print(f"[dim]Scanning extensions: {', '.join(ext_list)}[/dim]")

    # Scan for API calls
    scanner = CodeScanner(root_dir=path)

    with console.status("[bold green]Scanning code..."):
        calls = scanner.scan(extensions=ext_list)

    if not calls:
        console.print("[yellow]⚠️  No API calls with strayl:doc annotations found.[/yellow]")
        console.print("\nAdd annotations to your code:")
        console.print("[dim]# strayl:doc https://api.example.com/docs[/dim]")
        console.print("[dim]requests.post(url, json=data)[/dim]")
        sys.exit(0)

    console.print(f"[green]✓[/green] Found {len(calls)} annotated API call(s)\n")

    if verbose:
        _print_calls_table(calls)

    # Check API calls
    checker = ApiChecker(api_key=api_key)

    with console.status("[bold green]Checking against documentation..."):
        results = checker.check(calls)

    # Print results
    _print_results(results)

    # Exit with appropriate code
    has_errors = any(r.has_errors() or r.has_warnings() for r in results)
    sys.exit(1 if has_errors else 0)


@app.command()
def init(
    api_key: str = typer.Argument(..., help="Your Strayl API key"),
):
    """
    Initialize Strayl configuration in current directory.

    Example:
        strayl-lint init sk_live_xxx
    """
    config_path = Path(".strayl")

    if config_path.exists():
        overwrite = typer.confirm("Config file already exists. Overwrite?")
        if not overwrite:
            console.print("[yellow]Cancelled.[/yellow]")
            sys.exit(0)

    with open(config_path, 'w') as f:
        f.write(f"api_key={api_key}\n")

    console.print("[green]✓[/green] Created .strayl config file")
    console.print("\n[dim]Tip: Add .strayl to your .gitignore[/dim]")


@app.command()
def version():
    """Show version information."""
    from . import __version__
    console.print(f"strayl-lint version {__version__}")


def _print_calls_table(calls):
    """Print table of found API calls."""
    table = Table(title="Found API Calls", show_header=True)
    table.add_column("File", style="cyan")
    table.add_column("Line", justify="right", style="magenta")
    table.add_column("Documentation", style="blue")
    table.add_column("Method", style="green")

    for call in calls:
        table.add_row(
            call.file_path,
            str(call.line_number),
            call.doc_url,
            call.method or "?"
        )

    console.print(table)
    console.print()


def _print_results(results: List[CheckResult]):
    """Print check results."""
    console.print("[bold]Results:[/bold]\n")

    all_ok = True

    for result in results:
        if result.is_ok():
            console.print(f"[green]✅ {result.doc_url}[/green] - OK")
        elif result.has_warnings():
            all_ok = False
            console.print(f"[yellow]⚠️  {result.doc_url}[/yellow] - Warnings found:")
            for diff in result.diffs:
                console.print(f"   • {diff.get('message', str(diff))}")
        else:  # errors
            all_ok = False
            console.print(f"[red]❌ {result.doc_url}[/red] - Errors found:")
            for diff in result.diffs:
                console.print(f"   • {diff.get('message', diff.get('error', str(diff)))}")

    console.print()

    if all_ok:
        console.print(Panel(
            "[bold green]All API calls are up to date! 🎉[/bold green]",
            border_style="green"
        ))
    else:
        console.print(Panel(
            "[bold yellow]Some API calls may need updates.[/bold yellow]\n"
            "Review the warnings and errors above.",
            border_style="yellow"
        ))


if __name__ == "__main__":
    app()
