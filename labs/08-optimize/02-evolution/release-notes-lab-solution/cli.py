import typer

from hello import greet
from math_utils import add, multiply

app = typer.Typer(help="Release notes lab CLI")


@app.command()
def hello(name: str = typer.Argument("world")) -> None:
    typer.echo(greet(name))


@app.command()
def sum_values(a: float, b: float) -> None:
    typer.echo(add(a, b))


@app.command()
def product(a: float, b: float) -> None:
    typer.echo(multiply(a, b))


if __name__ == "__main__":
    app()
