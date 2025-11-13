from tools.template import template

import typer

app = typer.Typer(
    add_completion=True,
    help="Collection of CLI tools for development process"
)

app.add_typer(template.app, name="template")

if __name__ == "__main__":
    app()
