import regex as re

RE_HASHTAG = re.compile(r"\B#[\p{L}\p{M}\p{N}_]+", re.UNICODE)


def processor(text: str) -> str:
  """Remove hashtags without touching surrounding whitespace."""
  return RE_HASHTAG.sub("", text)


__all__ = ["processor"]
