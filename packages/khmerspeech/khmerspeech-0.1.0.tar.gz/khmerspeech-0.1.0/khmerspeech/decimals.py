import regex as re

from ._numbers import (
  decimal_fraction_words,
  integer_words,
  split_numeric_token,
)

RE_DECIMAL = re.compile(r"[-]?[\d\u17e0-\u17e9]+[.,][\d\u17e0-\u17e9]+")

DELIMITER_WORD = {".": "ចុច", ",": "ក្បៀស"}


def _verbalize(token: str) -> str:
  sign, integer_part, fractional_part, separator = split_numeric_token(token)
  if not fractional_part:
    return token

  delimiter = DELIMITER_WORD.get(separator or ".", "ចុច")
  integer_text = integer_words(integer_part, sep="▁")
  fraction_text = decimal_fraction_words(fractional_part, sep="▁")
  spoken = f"{integer_text}▁{delimiter}▁{fraction_text}"
  if sign == "-":
    spoken = f"ដក▁{spoken}"
  return spoken


def processor(text: str) -> str:
  """Verbalize decimal numbers found inside the text."""
  return RE_DECIMAL.sub(lambda m: _verbalize(m.group(0)), text)


__all__ = ["processor"]
