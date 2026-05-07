import typer

from rich.console import Console
from pathlib import Path
from importlib.metadata import version
from .core import process_folder, setup_logging, check_exiftool_existence

app = typer.Typer(
    name="gphotos_takeout_toolkit",
    help="Sort, merge metadata Google Takeout photos",
    no_args_is_help=True,
    rich_markup_mode="rich",
)
console = Console()

def version_callback(value: bool) -> None:
    """
    Function to get a version of the library.

    Parameters
    ----------
    value : bool
        Whether a version should be displayed.
    """
    if value:
        console.print(f"[bold]v{version('gphotos_takeout_toolkit')}[/]")
        raise typer.Exit()

@app.callback()
def main(
    version: bool = typer.Option(None, "--version", "-V", callback=version_callback, is_eager=True, help="Show version and exit.")
) -> None:
    """
    A callback that will display a version of the library.

    Parameters
    ----------
    version : bool
        Whether a version should be displayed.
    """
    pass

@app.command("organize")
def organize(
    input_path: Path = typer.Argument(..., help="Root of your Takeout folder."),
    destination_path: Path = typer.Argument(..., help="Destination folder."),
    owner_name: str = typer.Option("user", "--owner-name", "-o", help="Owner of the folders.", show_default=True),
    additional_file_move: bool = typer.Option(False, "--additional-file-move", "-a", help="Additionally move all files into one folder.", show_default=True),
    enable_verbosity: bool = typer.Option(False, "--enable-verbosity", "-v", help="Enable verbosity to see all the logs in the console.", show_default=True)
) -> None:
    """Command to sort, organize and merge metadata of the files."""
    setup_logging(enable_verbosity=enable_verbosity)

    if not check_exiftool_existence():
        return

    console.print("[bold green] Sorting and merging metadata...")
    process_folder(
        input_path=input_path,
        destination_path=destination_path,
        owner=owner_name,
        additional_file_move=additional_file_move
    )

    console.print("[bold green]✓ Done![/]")

if __name__ == "__main__":
    app()
