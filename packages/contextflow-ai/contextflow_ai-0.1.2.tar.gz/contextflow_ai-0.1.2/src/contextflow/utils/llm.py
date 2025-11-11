"""
Local LLM client using Ollama
"""

from google import genai
from google.genai import types
import json
import os
from typing import List, Dict


class LLMClient:
    """Lightweight LLM utility"""

    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model_name = "gemini-2.5-flash-lite"

    def generate_text(
        self, prompt: str, max_tokens: int = 500, temperature: float = 0.3
    ) -> str:
        """
        Generate text from a prompt (for summarization)

        Args:
            prompt: The prompt to send
            max_tokens: Maximum tokens in response
            temperature: Randomness (0=deterministic, 1=creative)

        Returns:
            Generated text
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0,
                ),
            )

            return response.text

        except Exception as e:
            raise Exception(f"LLM generation failed: {e}")

    def score_utility(self, text: str, goal: str) -> float:
        """
        Score message utility using an LLM

        Args:
            text: Message content
            goal: Agent goal for context

        Returns:
            Utility score 0-10
        """

        prompt = f"""Rate message relevance to goal (0-10 scale):

        Goal: {goal}

        Scoring guide:
        • 8-10: Specific facts, numbers, IDs, errors ("Error: timeout line 42" = 10)
        • 4-7: Questions, partial info ("Can you check status?" = 6)
        • 0-3: Acknowledgments, greetings ("Thanks!" = 1)

        Message: "{text}"

        Score (number only):"""

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0,
                response_mime_type="application/json",
                response_schema={
                    "type": "object",
                    "properties": {
                        "score": {
                            "type": "number",
                            "description": "Rating from 0-10",
                            "minimum": 0,
                            "maximum": 10,
                        }
                    },
                    "required": ["score"],
                },
            ),
        )
        result = json.loads(response.text)
        score = result["score"]

        return score

    def batch_score_utility(
        self, batch: List[Dict[str, str]], goal: str
    ) -> List[float]:
        """
        Score message utility using an LLM

        Args:
            text: Message content
            goal: Agent goal for context

        Returns:
            Utility score 0-10
        """

        formatted_messages = ""
        for i, msg in enumerate(batch, 1):
            role = msg.get("role", "unknown").capitalize()
            content = msg.get("content", "")
            # Truncate long messages to save prompt tokens?
            # formatted_messages += f"{i}. [{role}] {content[:200]}\n"
            formatted_messages += f"{i}. [{role}] {content}\n"

        prompt = f"""Rate message relevance to goal (0-10 scale):

        Goal: {goal}

        Scoring guide:
        • 8-10: Specific facts, numbers, IDs, errors ("Error: timeout line 42" = 10)
        • 4-7: Questions, partial info ("Can you check status?" = 6)
        • 0-3: Acknowledgments, greetings ("Thanks!" = 1)

        MESSAGES TO RATE:
        {formatted_messages}

        Return a JSON array with one score per message in order
        """
        response_schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "message_index": {
                        "type": "integer",
                        "description": "The message number (1-indexed)",
                    },
                    "score": {
                        "type": "number",
                        "description": "Utility score from 0-10",
                        "minimum": 0,
                        "maximum": 10,
                    },
                },
                "required": ["message_index", "score"],
            },
        }

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0,
                    response_mime_type="application/json",
                    response_schema=response_schema,
                ),
            )

            scores_data = json.loads(response.text)

            scores = self._extract_scores_from_json(scores_data, len(batch))

            return scores

        except Exception as e:
            print(
                f"Warning: Batch scoring failed ({e}). Using fallback scores."
            )
            return [5.0] * len(batch)

    def _extract_scores_from_json(
        self, scores_data: List[Dict], expected_count: int
    ) -> List[float]:
        """
        Extracts scores from the JSON array response.

        Args:
            scores_data: List of {"message_index": 1, "score": 8.5} objects
            expected_count: Number of messages we scored

        Returns:
            List of scores in the correct order
        """

        # Create a dict for quick lookup
        score_dict = {}
        for item in scores_data:
            idx = item.get("message_index")
            score = item.get("score", 5.0)
            if idx is not None:
                score_dict[idx] = max(0.0, min(10.0, float(score)))

        # Build the final list in order (1-indexed to 0-indexed)
        final_scores = []
        for i in range(1, expected_count + 1):
            final_scores.append(
                score_dict.get(i, 5.0)
            )  # Default to 5.0 if missing

        return final_scores
