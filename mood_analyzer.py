# mood_analyzer.py
"""
Rule based mood analyzer for short text snippets.

This class starts with very simple logic:
  - Preprocess the text
  - Look for positive and negative words
  - Compute a numeric score
  - Convert that score into a mood label
"""

from typing import List, Dict, Tuple, Optional
import re

from dataset import POSITIVE_WORDS, NEGATIVE_WORDS


class MoodAnalyzer:
    """
    A very simple, rule based mood classifier.
    """

    def __init__(
        self,
        positive_words: Optional[List[str]] = None,
        negative_words: Optional[List[str]] = None,
    ) -> None:
        # Use the default lists from dataset.py if none are provided.
        positive_words = positive_words if positive_words is not None else POSITIVE_WORDS
        negative_words = negative_words if negative_words is not None else NEGATIVE_WORDS

        # Store as sets for faster lookup.
        self.positive_words = set(w.lower() for w in positive_words)
        self.negative_words = set(w.lower() for w in negative_words)

    # ---------------------------------------------------------------------
    # Preprocessing
    # ---------------------------------------------------------------------

    def preprocess(self, text: str) -> List[str]:
        """
        Convert raw text into a list of tokens the model can work with.

        Improved:
          - Strips leading and trailing whitespace
          - Converts everything to lowercase
          - Removes punctuation
          - Splits on spaces
        """
        cleaned = text.strip().lower()
        cleaned = re.sub(r'[^\w\s]', '', cleaned)  # Remove punctuation
        tokens = cleaned.split()

        return tokens

    # ---------------------------------------------------------------------
    # Scoring logic
    # ---------------------------------------------------------------------

    def score_text(self, text: str) -> Dict[str, object]:
        """
        Compute a numeric "mood score" and track positive/negative hits.

        Positive words increase the score.
        Negative words decrease the score.

        Implemented improvements:
          - Handles simple negation for "not" and "never" before sentiment words.
          - Scores repeated positive/negative tokens as multiple signals.
          - Recognizes a small set of emojis as strong signals.
          - Detects basic sarcasm patterns (e.g., "absolutely love" with negative context).
        """
        tokens = self.preprocess(text)
        score = 0
        positive_hits: List[str] = []
        negative_hits: List[str] = []

        def polarity(token: str) -> int:
            if token in self.positive_words:
                return 1
            if token in self.negative_words:
                return -1
            if token in {":)", "😊", "😄", "💪", "🥳"}:
                return 2
            if token in {":(", "😢", "😞", "💀", "😡"}:
                return -2
            return 0

        for i, token in enumerate(tokens):
            p = polarity(token)

            if token in {"not", "never", "no"} and i + 1 < len(tokens):
                next_token = tokens[i + 1]
                p_next = polarity(next_token)
                if p_next != 0:
                    score -= p_next
                    if p_next > 0:
                        negative_hits.append(next_token)
                    else:
                        positive_hits.append(next_token)
                    continue

            score += p
            if p > 0:
                positive_hits.append(token)
            elif p < 0:
                negative_hits.append(token)

        # Sarcasm detection: if "absolutely" and "love" and negative words, penalize
        if "absolutely" in tokens and "love" in tokens and negative_hits:
            score -= 2  # Strong negative signal for sarcasm

        return {
            "score": score,
            "positive_hits": positive_hits,
            "negative_hits": negative_hits,
        }

    # ---------------------------------------------------------------------
    # Label prediction
    # ---------------------------------------------------------------------

    def predict_label(self, text: str) -> str:
        """
        Turn the numeric score for a piece of text into a mood label.

        Improved mapping:
          - Score takes precedence (handles sarcasm adjustments)
          - mixed only if score == 0 and both positive/negative signals exist
          - neutral if no signals
        """
        results = self.score_text(text)
        score = results["score"]
        pos = results["positive_hits"]
        neg = results["negative_hits"]

        if score > 0:
            return "positive"
        if score < 0:
            return "negative"
        if pos and neg:
            return "mixed"
        return "neutral"

    # ---------------------------------------------------------------------
    # Explanations (optional but recommended)
    # ---------------------------------------------------------------------

    def explain(self, text: str) -> str:
        """
        Return a short string explaining WHY the model chose its label.

        TODO:
          - Look at the tokens and identify which ones counted as positive
            and which ones counted as negative.
          - Show the final score.
          - Return a short human readable explanation.

        Example explanation (your exact wording can be different):
          'Score = 2 (positive words: ["love", "great"]; negative words: [])'

        The current implementation is a placeholder so the code runs even
        before you implement it.
        """
        results = self.score_text(text)
        score = results["score"]
        positive_hits = results["positive_hits"]
        negative_hits = results["negative_hits"]

        return (
            f"Score = {score} "
            f"(positive: {positive_hits or '[]'}, "
            f"negative: {negative_hits or '[]'})"
        )
