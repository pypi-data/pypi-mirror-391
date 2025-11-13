import typer

from . import serve

app = typer.Typer()

app.add_typer(serve.app)


def main():
    app()


if __name__ == "__main__":
    main()
