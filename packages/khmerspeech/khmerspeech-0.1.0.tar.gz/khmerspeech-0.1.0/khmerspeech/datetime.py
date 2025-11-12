import regex as re

from ._numbers import normalize_digits

RE_YEAR_FIRST = re.compile(
  r"(?P<year>[\d\u17e0-\u17e9]{4})(?P<sep>[/-])(?P<month>[\d\u17e0-\u17e9]{2})\2(?P<day>[\d\u17e0-\u17e9]{2})"
)

RE_DAY_FIRST = re.compile(
  r"(?P<day>[\d\u17e0-\u17e9]{2})(?P<sep>[/-])(?P<month>[\d\u17e0-\u17e9]{2})\2(?P<year>[\d\u17e0-\u17e9]{4})"
)

RE_TIME = re.compile(
  r"(?P<hour>[\d\u17e0-\u17e9]{1,2}):(?P<minute>[\d\u17e0-\u17e9]{2})\s*(?P<suffix>[AaPp][Mm])?"
)


def _format_date(match) -> str:
  groups = match.groupdict()
  year = normalize_digits(groups["year"])
  month = normalize_digits(groups["month"])
  day = normalize_digits(groups["day"])
  return f"{year} {month} {day}"


def _format_day_first(match) -> str:
  groups = match.groupdict()
  day = normalize_digits(groups["day"])
  month = normalize_digits(groups["month"])
  year = normalize_digits(groups["year"])
  return f"{day} {month} {year}"


def _format_time(match) -> str:
  groups = match.groupdict()
  hour = normalize_digits(groups["hour"])
  minute = normalize_digits(groups["minute"])
  suffix = groups.get("suffix") or ""
  suffix = suffix.upper()
  suffix_text = ""
  if suffix:
    suffix_text = "▁" + "▁".join(list(suffix))
  return f"{hour} {minute}{suffix_text}"


def date_processor(text: str) -> str:
  """Normalize numeric dates into space-separated tokens."""
  text = RE_YEAR_FIRST.sub(_format_date, text)
  text = RE_DAY_FIRST.sub(_format_day_first, text)
  return text


def time_processor(text: str) -> str:
  """Normalize clock times and verbalize AM/PM markers."""
  return RE_TIME.sub(_format_time, text)


__all__ = ["date_processor", "time_processor"]
