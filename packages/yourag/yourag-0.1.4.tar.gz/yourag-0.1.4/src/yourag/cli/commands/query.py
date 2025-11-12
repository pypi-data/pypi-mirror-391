from yourag.youtube.video import YTVideo
from yourag.transcript.base import TranscriptParser
from yourag.ai.embeddings import EmbeddingFactory
from yourag.ai.generators import GeneratorFactory
from yourag.vector_stores.chroma_store import ChromaVectorStore
from typing import Optional


def get_query_parser(subparsers):
    """
    Creates the query subparser.

    :param subparsers: The subparsers object from the main parser.
    :return: The query subparser.
    """
    query_parser = subparsers.add_parser("query", help="Query a YouTube video")
    video_group = query_parser.add_mutually_exclusive_group(required=True)
    video_group.add_argument(
        "-v",
        "--video-id",
        type=str,
        help="The ID of the YouTube video to query",
    )
    video_group.add_argument(
        "-u",
        "--video-url",
        type=str,
        help="The URL of the YouTube video to query",
    )
    video_group.add_argument(
        "-n",
        "--name",
        type=str,
        help="The name of the video collection to query",
    )
    query_parser.add_argument(
        "-q",
        "--query-text",
        required=True,
        type=str,
        help="The text query to search within the video content",
    )

    return query_parser


def query_video(args) -> None:
    """
    Query a YouTube video by its ID and a text query.

    :param video_id: The ID of the YouTube video to query.
    :param query_text: The text query to search within the video content.
    :param name: The name of the video collection to query.

    :return: None
    """
    # get video ID from URL if necessary
    if args.video_url or args.video_id:
        video_id = extract_video_id(args.video_url) if args.video_url else args.video_id
    else:
        video_id = None
        if not args.name:
            raise ValueError(
                "Either video-url, video-id or name must be provided to query a video."
            )

    embedding_generator = EmbeddingFactory.get_embedding_generator("openai")
    generator = GeneratorFactory.get_generator("openai")
    chroma_store = ChromaVectorStore()
    if video_id is None:
        collections = chroma_store.list_collections()
        matched_collection = None
        for collection_name in collections:
            collection = chroma_store.get_or_create_collection(collection_name)
            if collection.metadata.get("name") == args.name:
                matched_collection = collection_name
                break
        if not matched_collection:
            raise ValueError(f"No collection found with name: {args.name}")

        collection_name = matched_collection
    else:
        collection_name = f"video_{video_id}"  # default naming convention
    # Querying example
    print(f"Querying collection {collection_name} for query: '{args.query_text}'")
    query_embedding = embedding_generator.generate_embeddings(args.query_text)
    results = chroma_store.query_vectors(
        query_vector=query_embedding,
        top_k=3,
        collection_name=collection_name,
    )
    context = " ".join([text for doc in results["documents"] for text in doc])
    answer = generator.generate_answer(question=args.query_text, context=context)
    print("Answer:", answer)
