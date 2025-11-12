from yourag.ai.openai_llm import OpenAIEmbeddingGenerator


class EmbeddingFactory:
    """
    Factory class to get different embedding generators.
    """

    __available_embedding_generators = {
        "openai": OpenAIEmbeddingGenerator,
    }

    @classmethod
    def get_embedding_generator(cls, generator_name: str):
        """
        Get an instance of the specified embedding generator.

        :param generator_name: The name of the embedding generator.
        :return: An instance of the embedding generator.
        """

        if generator_name not in cls.__available_embedding_generators:
            raise ValueError(
                f"Embedding generator '{generator_name}' is not available. "
                f"Available generators: {list(cls.__available_embedding_generators.keys())}"
            )
        return cls.__available_embedding_generators.get(generator_name)()
