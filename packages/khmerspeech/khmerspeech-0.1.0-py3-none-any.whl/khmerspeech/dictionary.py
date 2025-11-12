from .khmer_dict_verbalize import dictionary_verbalize as _dictionary_verbalize


def dict_verbalize(text: str) -> str:
  """Expand measurement units, spellings, and verbatim mappings using the bundled dictionary."""
  return _dictionary_verbalize(text)


def processor(text: str) -> str:
  """Alias for compatibility with other processors."""
  return dict_verbalize(text)


__all__ = ["dict_verbalize", "processor"]
