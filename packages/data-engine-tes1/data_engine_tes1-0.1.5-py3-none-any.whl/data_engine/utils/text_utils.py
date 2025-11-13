from typing import Callable, List, Optional
import re


def get_words_from_document(
    text: str, token_func: Optional[Callable[[str], List[str]]] = None
) -> List[str]:
    """
    Extract words or tokens from the input text.

    :param text: Input raw text string.
    :param token_func: Optional tokenization function that takes text and returns a list of tokens.
                       If None, a simple whitespace tokenizer is used.
    :return: List of tokens (words or subwords).
    """
    if token_func is not None:
        # Use the provided tokenization function (e.g., SentencePiece)
        return token_func(text)
    else:
        # Fallback: basic whitespace + punctuation splitting
        # This regex splits on whitespace and punctuation, keeping words only
        tokens = re.findall(r"\b\w+\b", text.lower())
        return tokens
