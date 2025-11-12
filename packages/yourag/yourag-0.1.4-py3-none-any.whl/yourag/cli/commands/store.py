from yourag.vector_stores.chroma_store import ChromaVectorStore
from typing import Optional
from pprint import pprint


def list_collections(args) -> None:
    """
    List all collections in the vector store.
    """
    store = ChromaVectorStore()
    collections = store.list_collections()
    if not collections:
        print("No collections found in the vector store.")
        return
    print("Collections in the vector store:")
    for collection_name in collections:
        collection = store.get_or_create_collection(collection_name)
        pprint(collection.metadata, indent=4)
        print("-" * 40)


def get_store_parser(subparsers):
    """
    Creates the store subparser.

    :param subparsers: The subparsers object from the main parser.
    :return: The store subparser.
    """
    store_parser = subparsers.add_parser("store", help="Manage the vector store")
    # Additional subcommands for store can be added here
    store_parser.add_argument(
        "-ls",
        "--list",
        action="store_true",
        required=True,
        help="List all collections in the vector store",
    )

    return store_parser
