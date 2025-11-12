import regex as re

from ._numbers import integer_words, normalize_digits

RE_ORDINAL = re.compile(r"(?<![\w-])([\d\u17e0-\u17e9]+)(st|nd|rd|th)\b", re.IGNORECASE)


def _verbalize(match) -> str:
  number = normalize_digits(match.group(1))
  word = integer_words(number, sep="▁")
  return f"ទី▁{word}"


def processor(text: str) -> str:
  """Convert English ordinals (1st, 2nd, …) into Khmer ordinals."""
  return RE_ORDINAL.sub(_verbalize, text)


__all__ = ["processor"]
