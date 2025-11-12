from .khmer_normalize import normalize as _normalize


def processor(text: str) -> str:
  """Normalize Khmer text by cleaning Unicode artifacts and spacing."""
  return _normalize(text)


__all__ = ["processor"]
