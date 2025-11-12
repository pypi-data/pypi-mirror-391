import regex as re

from ._numbers import integer_words, split_numeric_token

RE_CARDINAL = re.compile(r"[-]?[\d\u17e0-\u17e9]+(?:[.,][\d\u17e0-\u17e9]+)?")


def _verbalize(token: str) -> str:
  sign, integer_part, fractional_part, separator = split_numeric_token(token)
  if not integer_part and not fractional_part:
    return token

  spoken = integer_words(integer_part, sep="▁")
  if fractional_part:
    spoken = f"{spoken}{separator}{integer_words(fractional_part, sep='▁')}"

  if sign == "-":
    spoken = f"ដក▁{spoken}"

  return spoken


def processor(text: str) -> str:
  """Convert digits inside the string into Khmer cardinals."""
  return RE_CARDINAL.sub(lambda m: _verbalize(m.group(0)), text)


__all__ = ["processor"]
