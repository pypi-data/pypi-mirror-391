"""
Message relevance and utility scoring
"""

from typing import List, Dict
from utils.llm import LLMClient
import numpy as np


class MessageScorer:
    def __init__(self):
        self._embedding_cache = {}
        self._llm_client = LLMClient()

    def _encode_text(self, text: str) -> np.ndarray:
        """Convert text to a vector embedding

        Args:
            text (str): Text to encode
        Returns:
            A 384-dimensional numpy array representing the text encoding
        """

        if text in self._embedding_cache:
            return self._embedding_cache[text]

        embedding = self.embedding_model.encode(
            text,
            convert_to_numpy=True,
            show_progress_bar=False,
        )

        self._embedding_cache[text] = embedding

        return embedding

    def _create_batches(self, messages: List[Dict[str, str]]):
        if len(messages) < 20:
            return [messages]

        return [messages[i : i + 20] for i in range(0, len(messages), 20)]

    def score_messages(
        self, messages: List[Dict[str, str]], agent_goal: str
    ) -> List[float]:
        """Scores messages based on how relevant they are to the agent's goal.

        Args:
            messages: A list of messages
            agent_goal: The goal of the agent
        Returns:
            A list scores such that scores[i] is the relevancy score of messages[i]
        """

        scores = []

        batches = self._create_batches(messages)

        for i, batch in enumerate(batches):
            batch_scores = self._llm_client.batch_score_utility(
                batch, agent_goal
            )
            scores += batch_scores

        for i in range(len(scores) - 1, max(-1, len(scores) - 6), -1):
            recency_bonus = 1.0
            scores[i] += recency_bonus

        return scores

    def _calculate_utility(self, text: str, goal: str) -> float:
        """Returns a utility score (0-10 scale)

        Args:
            text: String to evaluate the utility of
        Returns:
            Utility score of `text` between 0 and 10
        """
        text = text.strip()
        text_lower = text.lower()

        return self._llm_client.score_utility(text_lower, goal)
