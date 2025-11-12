import regex as re

from .khmer_number_verbalize import integer

KHMER_DIGIT_TRANSLATION = str.maketrans(
  {
    "០": "0",
    "១": "1",
    "២": "2",
    "៣": "3",
    "៤": "4",
    "៥": "5",
    "៦": "6",
    "៧": "7",
    "៨": "8",
    "៩": "9",
  }
)

THOUSAND_BLOCK_PATTERN = re.compile(r"^\d{1,3}(,\d{3})+$")


def normalize_digits(value: str) -> str:
  return value.translate(KHMER_DIGIT_TRANSLATION)


def split_numeric_token(token: str):
  token = token.strip()
  if not token:
    return "", "", "", ""

  sign = ""
  if token[0] in "+-":
    sign = token[0]
    token = token[1:]

  normalized = normalize_digits(token)
  decimal_mark = ""

  if "." in normalized:
    idx = normalized.rfind(".")
    integer_part = normalized[:idx]
    fractional_part = normalized[idx + 1 :]
    decimal_mark = "."
  elif "," in normalized:
    if THOUSAND_BLOCK_PATTERN.fullmatch(normalized):
      integer_part = normalized.replace(",", "")
      fractional_part = ""
    else:
      idx = normalized.rfind(",")
      integer_part = normalized[:idx]
      fractional_part = normalized[idx + 1 :]
      decimal_mark = ","
  else:
    integer_part = normalized
    fractional_part = ""

  integer_part = re.sub(r"[^\d]", "", integer_part)
  fractional_part = re.sub(r"[^\d]", "", fractional_part)

  return sign, integer_part or "0", fractional_part, decimal_mark


def integer_words(value: str, sep: str = "▁") -> str:
  return integer(int(value), sep=sep)


def decimal_fraction_words(value: str, sep: str = "▁") -> str:
  if not value:
    return ""

  leading_zero_count = len(value) - len(value.lstrip("0"))
  parts = ["សូន្យ"] * leading_zero_count
  remainder = value[leading_zero_count:]

  if remainder:
    if len(remainder) > 3:
      parts.extend(integer(int(d), sep=sep) for d in remainder)
    else:
      parts.append(integer(int(remainder), sep=sep))

  return sep.join(parts) if parts else ""


def currency_fraction_words(value: str, sep: str = "▁", precision: int | None = None) -> str:
  if not value:
    return ""

  cleaned = value
  if precision is not None:
    cleaned = (cleaned + "0" * precision)[:precision]

  cleaned = cleaned.lstrip("0")
  if not cleaned:
    return ""

  if len(cleaned) > 3:
    return sep.join(integer(int(d), sep=sep) for d in cleaned)

  return integer(int(cleaned), sep=sep)
