import regex as re

from ._numbers import currency_fraction_words, integer_words, split_numeric_token
from .string_utils import overwrite_spans

USD_SYMBOLS = {"$", "USD", "ដុល្លារ"}
KHR_SYMBOLS = {"៛", "KHR", "រៀល"}

CURRENCY_PATTERN = re.compile(
  r"(?P<prefix>\$|USD|ដុល្លារ|៛|KHR|រៀល)\s?(?P<amount_prefix>[\d\u17e0-\u17e9][\d\u17e0-\u17e9,\.]*)"
  r"|(?P<amount_suffix>[\d\u17e0-\u17e9][\d\u17e0-\u17e9,\.]*)\s?(?P<suffix>\$|USD|ដុល្លារ|៛|KHR|រៀល)"
)


def _verbalize_usd(amount: str) -> str:
  sign, integer_part, fractional_part, _ = split_numeric_token(amount)
  integer_text = integer_words(integer_part, sep="▁")
  cents = currency_fraction_words(fractional_part, sep="▁", precision=2)

  if cents:
    segments = [f"{integer_text}ដុល្លារ", f"{cents}សេន"]
  else:
    segments = [f"{integer_text}▁ដុល្លារ"]

  spoken = "▁".join(segments)
  if sign == "-":
    spoken = f"ដក▁{spoken}"
  return spoken


def _verbalize_khr(amount: str, separator: str) -> str:
  sign, integer_part, fractional_part, sep_hint = split_numeric_token(amount)
  integer_text = integer_words(integer_part, sep="▁")

  if fractional_part:
    delimiter = "ចុច" if (sep_hint or separator) != "," else "ក្បៀស"
    fraction_text = currency_fraction_words(fractional_part, sep="▁")
    number_text = f"{integer_text}{delimiter}{fraction_text}"
  else:
    number_text = integer_text

  spoken = f"{number_text}▁រៀល"
  if sign == "-":
    spoken = f"ដក▁{spoken}"
  return spoken


def _verbalize_currency(amount: str, symbol: str) -> str | None:
  if symbol in USD_SYMBOLS:
    return _verbalize_usd(amount)
  if symbol in KHR_SYMBOLS:
    return _verbalize_khr(amount, separator=symbol)
  return None


def processor(text: str) -> str:
  """Verbalize Cambodian currency amounts (USD and riel)."""
  replacements = []
  for match in CURRENCY_PATTERN.finditer(text):
    symbol = match.group("prefix") or match.group("suffix")
    amount = match.group("amount_prefix") or match.group("amount_suffix")
    spoken = _verbalize_currency(amount, symbol)
    if spoken:
      replacements.append((match.start(), match.end(), spoken))
  return overwrite_spans(text, replacements)


__all__ = ["processor"]
