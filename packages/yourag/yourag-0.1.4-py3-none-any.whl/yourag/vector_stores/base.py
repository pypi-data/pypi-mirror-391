from abc import ABC, abstractmethod


class VectorStore(ABC):
    """
    This is a base class for vector stores.
    It defines the interface that all vector store implementations must follow.
    """

    @abstractmethod
    def add_vectors(self, vectors: list, metadata: list) -> None:
        """
        Adds vectors along with their associated metadata to the vector store.

        :param vectors: A list of vectors to be added.
        :param metadata: A list of metadata corresponding to each vector.
        """
        pass

    @abstractmethod
    def query_vectors(self, query_vector: list, top_k: int) -> list:
        """
        Queries the vector store for the top_k most similar vectors to the given query_vector.

        :param query_vector: The vector to query against the vector store.
        :param top_k: The number of top similar vectors to retrieve.
        :return: A list of the top_k most similar vectors and their metadata.
        """
        pass

    @abstractmethod
    def delete_vectors(self, vector_ids: list) -> None:
        """
        Deletes vectors from the vector store based on their IDs.

        :param vector_ids: A list of vector IDs to be deleted.
        """
        pass

    @abstractmethod
    def clear_store(self) -> None:
        """
        Clears all vectors and metadata from the vector store.
        """
        pass


class StoreFactory:
    """
    Factory class to create instances of VectorStore implementations.
    """

    __available_stores = {
        "FAISSVectorStore": "yourag.vector_stores.faiss_store.FAISSVectorStore",
        "PineconeVectorStore": "yourag.vector_stores.pinecone_store.PineconeVectorStore",
        "AtlasVectorStore": "yourag.vector_stores.atlas_store.AtlasVectorStore",
    }

    def get_available_stores(self) -> list:
        """
        Returns a list of available vector store implementations.

        :return: A list of available vector store names.
        """
        return list(self.__available_stores.keys())

    @abstractmethod
    def create_store(self, store_name: str, **kwargs) -> VectorStore:
        """
        Creates an instance of the specified vector store implementation.

        :param store_name: The name of the vector store implementation to create.
        :return: An instance of the specified VectorStore.
        """
        if store_name not in self.__available_stores:
            raise ValueError(f"Unknown store: {store_name}")

        module_path = self.__available_stores[store_name]
        module = __import__(module_path, fromlist=[store_name])
        store_class = getattr(module, store_name)
        return store_class(**kwargs)
