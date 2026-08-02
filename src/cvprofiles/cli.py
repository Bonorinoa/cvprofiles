"""Thin Typer CLI entrypoint. State commands land with M2+."""

from __future__ import annotations

import typer

from cvprofiles import __version__

app = typer.Typer(
    name="cvprofiles",
    help="Construct-validity profiles: admissible sets and construct-identified ranges.",
    no_args_is_help=True,
    add_completion=False,
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"cvprofiles {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Show package version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    """cvprofiles CLI (spine states wire up after M1)."""


if __name__ == "__main__":
    app()
