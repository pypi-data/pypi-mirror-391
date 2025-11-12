from .khmer_phonenumbers import processor as _processor


def processor(text: str, *, chunk_size: int = 2, delimiter: str = "▁", country_code: str = "KH") -> str:
  """Verbalize Khmer phone numbers by chunking digits."""
  return _processor(text, chunk_size=chunk_size, delimiter=delimiter, country_code=country_code)


__all__ = ["processor"]
