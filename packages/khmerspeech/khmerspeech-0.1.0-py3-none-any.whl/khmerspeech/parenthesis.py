import regex as re

RE_PAREN = re.compile(r"\s*\((.*?)\)\s*|\s*\[(.*?)\]\s*")
RE_SPACE = re.compile(r"\s{2,}")


def processor(text: str) -> str:
  """Remove any content wrapped inside parentheses or brackets."""
  cleaned = RE_PAREN.sub(" ", text)
  cleaned = RE_SPACE.sub(" ", cleaned)
  return cleaned.strip()


__all__ = ["processor"]
