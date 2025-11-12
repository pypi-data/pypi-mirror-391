import click


from .dependencies import initialise_dependencies, get_config_path, write_api_token_to_config
from .ui.app import TailscaleTui


@click.command()
@click.argument("token", default=None, required=False)
def run(token) -> None:
    if token:
        config_path = get_config_path()
        write_api_token_to_config(config_path, token)

    dependencies = initialise_dependencies()
    app = TailscaleTui(deps=dependencies)
    app.run()
