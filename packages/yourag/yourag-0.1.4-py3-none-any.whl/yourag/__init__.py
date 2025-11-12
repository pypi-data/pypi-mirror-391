from yourag.utils.file_utils import get_root_project
from yourag.vector_stores.chroma_store import ChromaVectorStore
from yourag.ai.embeddings import EmbeddingFactory
from yourag.ai.generators import GeneratorFactory
from yourag.youtube.client import YouTubeClient
from yourag.youtube.video import YTVideo
from yourag.transcript.base import TranscriptParser
from dotenv import load_dotenv
import os
import uuid


def main() -> None:
    load_dotenv()
    yt_client = YouTubeClient()
    video = YTVideo(video_id="_kvuw74LnTw", client=yt_client)
    transcript = video.get_transcript()
    print("Transcript retrieved with", len(transcript.entries), "entries.")
    for entry in transcript.entries[:5]:
        print(
            f"[{entry.start} - {entry.end}]: {entry.text} - Duration: {entry.duration}\n"
        )

    parser = TranscriptParser(transcript)
    chunks = parser.get_chunks(chunk_size=50, overlap=0.2)
    print(f"Generated {len(chunks)} chunks from the transcript.")
    for chunk in chunks:
        print(
            f"Duration: {chunk['duration']} - [{chunk['start']} - {chunk['end']}]: {chunk['text']}\n"
        )
    embedding_generator = EmbeddingFactory.get_embedding_generator("openai")
    generator = GeneratorFactory.get_generator("openai")
    chroma_store = ChromaVectorStore()
    chunks = parser.get_chunks(chunk_size=50, overlap=0.2)
    # embeddings =  {
    #     "ids": [],
    #     "embeddings": [],
    #     "documents": [],
    #     "metadatas": [],
    # }
    # for chunk in chunks:
    #     embedding = embedding_generator.generate_embeddings(chunk["text"])
    #     embeddings["ids"].append(str(uuid.uuid4()))
    #     embeddings["embeddings"].append(embedding)
    #     embeddings["documents"].append(chunk["text"])
    #     embeddings["metadatas"].append({"start": str(chunk["start"]), "end": str(chunk["end"]), "duration": str(chunk["duration"])})

    collection_name = f"video_{video.video_id}"
    # Use the chroma_store for vector operations
    # chroma_store.add_vectors(
    #     ids=embeddings["ids"],
    #     embeddings=embeddings["embeddings"],
    #     documents=embeddings["documents"],
    #     collection_name=collection_name,
    #     metadatas=embeddings["metadatas"],
    # )

    # Querying example
    query_text = "What is the main topic of the video?"
    query_embedding = embedding_generator.generate_embeddings(query_text)
    results = chroma_store.query_vectors(
        query_vector=query_embedding,
        top_k=3,
        collection_name=collection_name,
    )
    # print("Relevant documents:", results)
    print(len(results["documents"]))
    for result in results["documents"]:
        print(result)
        print("----")

    context = " ".join([text for doc in results["documents"] for text in doc])
    answer = generator.generate_answer(question=query_text, context=context)
    print("Generated Answer:", answer)
    # Generating text based on retrieved documents
    print("Context for answer generation:", context)
    answer = generator.generate_answer(question=query_text, context=context)
    print("Generated Answer:", answer)
