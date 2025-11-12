from yourag.cli.commands.base import CLI
from dotenv import load_dotenv


def cli():
    load_dotenv()
    cli = CLI()
    cli.run()
