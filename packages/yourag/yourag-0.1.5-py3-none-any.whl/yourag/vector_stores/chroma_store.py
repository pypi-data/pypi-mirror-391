from yourag.vector_stores.base import VectorStore
from yourag.core.configs.chroma_config import persistent_client_path
import chromadb
from typing import Optional, List, Dict, Any
import os


class ChromaVectorStore(VectorStore):
    """
    Implementation of VectorStore using Chroma as the backend.
    """

    def __init__(self, collection_name: Optional[str] = None):
        """
        Initializes the ChromaVectorStore with the specified collection name.

        :param collection_name: The name of the Chroma collection to use.
        """
        self.collection_name = collection_name
        print(f"Starting Chroma persistent client...{persistent_client_path}")
        self.__start_persistent_client(persistent_client_path)

    def __start_persistent_client(self, client_path: str):
        """
        Starts the persistent Chroma client.

        :param client_path: The path to the persistent client.
        """
        if not os.path.exists(client_path):
            os.makedirs(client_path)

        self.client = chromadb.PersistentClient(client_path)

    def add_vectors(
        self,
        ids: List[str],
        embeddings: List[Dict[str, Any]],
        documents: List[str],
        collection_name: str,
        metadatas: Optional[List[Dict[str, Any]]] = None,
        collection_metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Adds vectors along with their associated metadata to the Chroma
        vector store.

        :param vectors: A list of vectors to be added.
        :param metadata: A list of metadata corresponding to each vector.
        :param collection_name: The name of the Chroma collection to use.
        """
        # collection_name override if provided
        if collection_name:
            self.collection_name = collection_name

        if not self.collection_name:
            raise ValueError("Collection name must be provided to add vectors.")

        collection = self.get_or_create_collection(
            self.collection_name, collection_metadata
        )

        collection.add(
            ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas
        )

    def query_vectors(
        self, query_vector: list, top_k: int, collection_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Queries the Chroma vector store for the top_k most similar
        vectors to the given query_vector.

        :param query_vector: The vector to query against the vector store.
        :param top_k: The number of top similar vectors to retrieve.
        :param collection_name: The name of the Chroma collection to use.
        :return: A list of the top_k most similar vectors and their metadata.
        """
        if not collection_name:
            raise ValueError("Collection name must be set to query vectors.")

        collection = self.get_or_create_collection(collection_name)

        results = collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
            include=["metadatas", "documents", "distances"],
        )

        return results

    def delete_vectors(
        self, vector_ids: List[str], collection_name: Optional[str] = None
    ) -> None:
        """
        Deletes vectors from the Chroma vector store based on their IDs.

        :param vector_ids: A list of vector IDs to be deleted.
        :param collection_name: The name of the Chroma collection to use.
        """
        if not collection_name:
            raise ValueError("Collection name must be set to delete vectors.")

        collection = self.get_or_create_collection(collection_name)

        collection.delete(ids=vector_ids)

    def get_or_create_collection(
        self, collection_name: str, metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Retrieves an existing collection or creates a new one if it doesn't exist.

        :param collection_name: The name of the Chroma collection.
        :param metadata: Optional metadata for the collection.
        :return: The Chroma collection object.
        :raises chromadb.errors.CollectionNotFoundError: If the collection does not
        exist and cannot be created.
        """
        try:
            collection = self.client.get_collection(name=collection_name)
        except Exception as e:
            # For now the user has to pass the vector embeddings.
            print(
                f"Collection '{collection_name}' not found. Creating a new collection. Error: {e}"
            )
            collection = self.client.create_collection(
                name=collection_name, metadata=metadata, embedding_function=None
            )
        return collection

    def list_collections(self) -> List[str]:
        """
        Lists all collections in the Chroma vector store.

        :return: A list of collection names.
        """
        collections = self.client.list_collections()
        return [collection.name for collection in collections]

    def delete_collection(self, collection_name: str) -> None:
        """
        Deletes a collection from the Chroma vector store.

        :param collection_name: The name of the Chroma collection to delete.
        """
        try:
            self.client.delete_collection(name=collection_name)
        except Exception as e:
            print(f"Error deleting collection '{collection_name}': {e}")

    def delete_vectors(self, vector_ids: list) -> None:
        """
        Deletes vectors from the Chroma vector store based on their IDs.

        :param vector_ids: A list of vector IDs to be deleted.
        """
        # Implementation for deleting vectors from Chroma
        pass

    def clear_store(self) -> None:
        """
        Clears all vectors and metadata from the Chroma vector store.
        """
        # Implementation for clearing the Chroma store
        pass
