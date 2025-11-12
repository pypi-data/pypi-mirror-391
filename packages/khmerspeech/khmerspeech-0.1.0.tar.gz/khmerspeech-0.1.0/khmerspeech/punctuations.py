import regex as re

MULTI_PUNCT = re.compile(r"([៙៚៖!?។៕])\1+")
SPACE_AFTER_PUNCT = re.compile(r"([៙៚៖!?។៕])(?!\s|$)")


def processor(text: str) -> str:
  """Collapse repeated sentence terminators and ensure spacing."""
  cleaned = MULTI_PUNCT.sub(r"\1", text)
  cleaned = SPACE_AFTER_PUNCT.sub(r"\1 ", cleaned)
  return cleaned


__all__ = ["processor"]
