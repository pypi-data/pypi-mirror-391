from typing import Callable, Iterable

from .khmer_repeater_verbalize import repeaters_verbalize

Tokenizer = Callable[[str], Iterable[str]]


def processor(text: str, *, tokenizer: Tokenizer | None = None, sep: str = "▁") -> str:
  """Expand Khmer iteration marks (ៗ) using the provided tokenizer."""
  return repeaters_verbalize(text, sep=sep, tokenizer=tokenizer)


__all__ = ["processor"]
