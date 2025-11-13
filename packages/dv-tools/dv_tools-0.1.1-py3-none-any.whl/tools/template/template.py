import re

import typer
from jinja2 import Environment, FileSystemLoader, meta

app = typer.Typer(
    no_args_is_help=True,
    add_completion=True,
    help="Tools for creation of jinja2 templates"
)


@app.command(help="Create Odoo database")
def generate():
    """
    Create templates from Jinja2 templates in the current directory.
    """

    # Load templates from the current directory
    env = Environment(loader=FileSystemLoader('.'))

    templates = {}
    template_index = 1

    for template in env.list_templates():
        if template.endswith('.j2'):
            templates[template_index] = template
            template_index += 1

    if template_index == 1:
        typer.echo("No templates found in the current directory.")
        exit(0)

    templates[99] = "Exit"

    # Keep creating templates until the user exits
    while True:
        print("-- Choose template --")
        for i, template in templates.items():
            print(f"{i}: {template}")

        # Choose template
        template_id = int(input("Template ID: "))
        if template_id == 99:
            exit()

        template_name = templates[template_id]

        # Read the template file
        with open(template_name, 'r', encoding='utf-8') as f:
            source = f.read()

        # Parse template
        parsed_content = env.parse(source)

        # Find undeclared variables
        variables = meta.find_undeclared_variables(parsed_content)

        # Extract default values from template (if any)
        default_values = {}
        for match in re.finditer(r'{{\s*(\w+)\s*\|\s*default\([\'"]([^\'"]*)[\'"]', source):
            var_name = match.group(1)
            default_val = match.group(2)
            default_values[var_name] = default_val

        values = {}

        print("\n-- Enter values for the variables --")
        for v in variables:
            if v in default_values:
                user_input = input(f"Enter value for {v} [default: {default_values[v]}]: ").strip()
                values[v] = user_input or default_values[v]
            else:
                while True:
                    values[v] = input(f"Enter value for {v}: ")
                    if values[v] != "":
                        break
                    else:
                        print("Value cannot be empty.")

        extension = template_name.split(".")[-2]
        original_filename = template_name.split(".")[0]
        print("\n-- Enter output filename (without extension) --")
        filename = f"{input(f"Enter output filename (without extension) [default: {original_filename}]: ").strip()}"
        if filename == "":
            filename = original_filename

        with open(f"{filename}.{extension}", 'w', encoding='utf-8') as f:
            f.write(env.get_template(template_name).render(values))


if __name__ == "__main__":
    app()
