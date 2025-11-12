from yourag.youtube.models import Transcript
from typing import List, Dict, Any
import re
import uuid


class TranscriptParser:
    """
    Parses and processes the transcript data.
    """

    def __init__(self, transcript: Transcript):
        """
        Initializes the TranscriptParser with a transcript object.

        :param transcript: Transcript object obtained from YouTube API.
        :return: None
        """
        self.transcript = transcript.entries  # List of TranscriptEntry objects
        print(f"TranscriptParser initialized with {len(self.transcript)} entries.")

    def __get_word_count(self, text: str) -> int:
        """
        Returns the number of words in the given text.
        """
        words = re.findall(r"\b\w+\b", text)
        return len(words)

    def get_chunks(
        self, chunk_size: int = 300, overlap: float = 0.1
    ) -> List[Dict[str, Any]]:
        """
        Get chunks of the transcript.
        :param chunk_size: Number of words in each chunk
        :param overlap: Fraction of overlap between chunks (0.1 means 10% overlap)
        :return: List of chunks, each chunk is a dict with "text", "start", "duration"
        """
        # Split the transcript into chunks of specified size with overlap
        word_count = 0
        chunks = []
        chunk = []
        duration = 0.0
        overlap_count = int(chunk_size * overlap)
        t_start = self.transcript[0].start
        for n, t in enumerate(self.transcript):
            word_count += self.__get_word_count(t.text)
            chunk.append(t.text)
            if word_count >= chunk_size:
                chunk_text = " ".join(chunk)
                chunks.append(
                    {
                        "text": chunk_text,
                        "duration": t.end - t_start,
                        "start": t_start,
                        "end": t.end,
                    }
                )
                # Reset for next chunk, keeping overlap
                t_start = self.transcript[n].start
                # next chunk starts with the last 'overlap_count' words of the current chunk
                chunk = (
                    [" ".join(chunk_text.split()[-overlap_count:])]
                    if overlap_count < len(chunk_text.split())
                    else chunk
                )
                word_count = 0

            # handling the last chunk
            if duration > 0 and n == len(self.transcript) - 1:
                chunk_text = " ".join(chunk)
                chunks.append(
                    {
                        "text": chunk_text,
                        "duration": t.end - t_start,
                        "start": t_start,
                        "end": t.end,
                    }
                )
        return chunks
