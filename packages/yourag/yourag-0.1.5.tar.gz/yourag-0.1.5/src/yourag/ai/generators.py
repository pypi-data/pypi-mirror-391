from yourag.ai.openai_llm import OpenAIGenerator


class GeneratorFactory:

    __available_generators = {
        "openai": OpenAIGenerator,
    }

    @classmethod
    def get_generator(cls, generator_name: str):
        """
        Get an instance of the specified generator.

        :param generator_name: The name of the generator.
        :return: An instance of the generator.
        """

        if generator_name not in cls.__available_generators:
            raise ValueError(
                f"Generator '{generator_name}' is not available. "
                f"Available generators: {list(cls.__available_generators.keys())}"
            )
        return cls.__available_generators.get(generator_name)()
