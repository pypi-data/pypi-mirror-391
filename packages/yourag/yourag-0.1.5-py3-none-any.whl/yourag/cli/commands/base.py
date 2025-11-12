from yourag.cli.commands.ingest import get_ingest_parser, ingest_video
from yourag.cli.commands.store import get_store_parser, list_collections
from yourag.cli.commands.query import get_query_parser, query_video
import argparse


class CLI:
    """
    Factory class for CLI commands.
    """

    __available_subcommands = {
        "ingest": get_ingest_parser,
        "query": get_query_parser,
        "store": get_store_parser,
    }

    def __init__(self):
        self.parser = argparse.ArgumentParser(description="YourAG CLI")
        self.subparsers = self.parser.add_subparsers(dest="command")
        self.__build_subparsers()
        self.args = self.parser.parse_args()

    def __build_subparsers(self):
        """
        Build all available subparsers.
        """
        for command, builder in self.__available_subcommands.items():
            builder(self.subparsers)

    def run(self):
        """
        Run the CLI with the provided arguments.
        """
        self.execute(self.args)

    def execute(self, args):
        """
        Execute the command with the given arguments.
        """
        command_map = {
            "ingest": ingest_video,
            "query": query_video,
            "store": list_collections,
        }
        command_func = command_map.get(args.command)
        if command_func:
            command_func(args)
        else:
            print(f"Unknown command: {args.command}")
