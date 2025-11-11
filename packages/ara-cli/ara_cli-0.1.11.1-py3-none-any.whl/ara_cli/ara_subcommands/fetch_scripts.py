import typer
from ara_cli.commands.fetch_scripts_command import FetchScriptsCommand

def register(app: typer.Typer):
    @app.command(name="fetch-scripts", help="Fetch global scripts into your config directory.")
    def fetch_scripts():
        command = FetchScriptsCommand()
        command.execute()
