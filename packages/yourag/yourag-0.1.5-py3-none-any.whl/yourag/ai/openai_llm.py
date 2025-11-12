from openai import OpenAI
import os
from yourag.ai import prompts
from yourag.ai.base import EmbeddingModel, LLM
from typing import Optional, List


class OpenAIGenerator(LLM):
    """
    This class interacts with OpenAI's API to generate text.
    """

    def __init__(self, model_name: str = "gpt-4"):
        """
        Initializes the OpenaAIGenerator with the specified model name.

        :param model_name: The name of the OpenAI model to use.
        """
        self.model_name = model_name
        self.openai_client = get_openai_client()

    def generate_answer(self, question: str, context: str) -> str:
        """
        Generate an answer using OpenAI's GPT model based on the question and context.

        :param question: The input question.
        :param context: The relevant context.
        :return: The generated answer.
        """
        prompt = f"Context: {context}\n\nQuestion: {question}\nAnswer:"  # Maybe improve with LangChain prompt templates
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": prompts.YOUTUBE_COMMENT_REPLY_PROMPT,
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=150,
                n=1,
                stop=None,
                temperature=0.7,
            )
            answer = response.choices[0].message.content.strip()
            return answer
        except Exception as e:
            print(f"Error generating answer: {e}")
            return "I'm sorry, I couldn't generate an answer at this time."


class OpenAIEmbeddingGenerator(EmbeddingModel):
    """
    This class generates embeddings using OpenAI's API.
    """

    def __init__(self, model_name: str = "text-embedding-ada-002"):
        """
        Initializes the OpenAIEmbeddingGenerator with the specified model name.

        :param model_name: The name of the OpenAI embedding model to use.
        """
        self.model_name = model_name
        self.openai_client = get_openai_client()

    def generate_embeddings(self, text: str) -> Optional[List[float]]:
        """
        Get embeddings for a given text using OpenAI API.

        :param text: The input text.
        :return: The embeddings as a list of floats.
        """
        try:
            response = self.openai_client.embeddings.create(
                input=[text], model=self.model_name
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error getting embeddings: {e}")
            return None


def get_openai_client() -> OpenAI:
    """
    Get the OpenAI client.
    """
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if OPENAI_API_KEY is None:
        print("OPENAI_API_KEY is not set in environment variables.")
        return None
    return OpenAI(api_key=OPENAI_API_KEY)


def identify_category(user_prompt: str, openai_client) -> str:
    """
    Identify the category of a comment using OpenAI's GPT model.

    :param user_prompt: The input prompt.
    :param openai_client: The OpenAI client.
    :return: The generated response.
    """
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": prompts.CLASSIFICATION_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7,
        )
        print(response)
        answer = response.choices[0].message.content.strip()
        return answer
    except Exception as e:
        raise RuntimeError(f"Error calling LLM: {e}")


def generate_answer(question: str, context: str, openai_client) -> str:
    """
    Generate an answer using OpenAI's GPT model based on the question and context.

    :param question: The input question.
    :param context: The relevant context.
    :param openai_client: The OpenAI client.
    :return: The generated answer.
    """
    prompt = f"Context: {context}\n\nQuestion: {question}\nAnswer:"
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": prompts.YOUTUBE_COMMENT_REPLY_PROMPT,
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7,
        )
        print(response)
        answer = response.choices[0].message.content.strip()
        return answer
    except Exception as e:
        print(f"Error generating answer: {e}")
        return "I'm sorry, I couldn't generate an answer at this time."
