from .text_url_verbalize import transform_urls_emails as _transform


def processor(text: str) -> str:
  """Verbalize URLs and email addresses."""
  return _transform(text)


__all__ = ["processor"]
