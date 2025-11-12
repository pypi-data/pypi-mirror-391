import os
import pathlib
import regex as re
from urlextract import URLExtract

domain_lookup = {
  "kh": "k▁h",
  "gmail": "g▁mail",
  "edu": "EDU",
  "org": "ORG",
  "gov": "gov",
  "per": "PER",
  "io": "IO",
  "us": "US",
  "sg": "SG",
  "ru": "RU",
  "th": "TH",
}

_CACHE_DIR = pathlib.Path(__file__).with_name("_url_cache")
os.makedirs(_CACHE_DIR, exist_ok=True)

url_extractor = URLExtract(
  extract_email=True,
  extract_localhost=True,
  cache_dir=str(_CACHE_DIR),
)


def url_verbalize(url: str) -> str:
  url = re.sub(r"https?:\/\/", "", url, re.IGNORECASE)
  paths = url.split(".")
  return " dot ".join(
    map(
      lambda x: domain_lookup[x.lower()] if x.lower() in domain_lookup else x,
      paths,
    )
  )


def email_verbalize(email: str) -> str:
  username, domain = email.split("@")
  return f"{username} at {url_verbalize(domain)}"


def transform_urls_emails(text: str) -> str:
  if url_extractor.has_urls(text):
    for url in url_extractor.gen_urls(text):
      if "@" in url:
        text = text.replace(url, email_verbalize(url))
        continue
      text = text.replace(url, url_verbalize(url))
  return text
