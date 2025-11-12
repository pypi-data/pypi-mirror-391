import regex as re

RE_QUOTES = re.compile(r'[\"“”«»„‟”]+')


def processor(text: str) -> str:
  """Strip enclosing quotation marks while keeping the content."""
  return RE_QUOTES.sub("", text)


__all__ = ["processor"]
