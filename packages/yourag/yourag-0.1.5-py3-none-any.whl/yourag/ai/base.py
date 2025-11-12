from abc import ABC, abstractmethod
from typing import Optional, List


class EmbeddingModel(ABC):
    """
    Abstract base class for embedding models.
    """

    def __init__(self):
        pass

    @abstractmethod
    def generate_embeddings(self, text: str):
        pass


class LLM(ABC):
    """
    Abstract base class for language models.
    """

    def __init__(self):
        pass

    @abstractmethod
    def generate_answer(self) -> str:
        """
        Generates text based on the provided prompts.
        """
        pass
