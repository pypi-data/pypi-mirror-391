import regex as re 
from . import (
  ascii_lines,
  cardinals,
  dictionary,
  currency,
  datetime,
  decimals,
  hashtags,
  license_plate,
  normalize,
  ordinals,
  parenthesis,
  phone_numbers,
  punctuations,
  repeater,
  urls,
  quotings,
)
from .dictionary import dict_verbalize


RE_HASHTAGS = re.compile(r"\B(\#[a-zA-Z]+\b)")
RE_ENCLOSED_PARENTHESIS_BACKETS = re.compile(r"\s*\((.*?)\)\s*|\s*\[(.*?)\]\s*")
RE_GENERIC_NUMBER = re.compile(r"\d+\.?\d*")
RE_NUMBER_COMMAS = re.compile(r"(\d+)\,(\d+)")
RE_USELESS_COMMAS = re.compile(r"\s*\,\s*")
RE_ORDINAL_NUMBER = re.compile(r"^([\d\u17e0-\u17e9]+)\.\s")
RE_SPACING_COMMAS = re.compile(
  r"([^0-9\u17e0-\u17e9])[,]+([^0-9\u17e0-\u17e9]|$)"
)  # abc,abc
RE_NUM_LEADING_ZEROS = re.compile(r"\.([\u17e00]+)([\d\u17e0-\u17e9]+)")

def leading_zeros_replacer(m):
  padded_zeros = "▁".join(m[1])
  return f".▁{padded_zeros}▁{m[2]}"



def tts_normalize(text: str) -> str:
    text = normalize.processor(text)
    text = phone_numbers.processor(text, chunk_size=3)
    text = datetime.date_processor(text)
    text = datetime.time_processor(text)
    text = urls.processor(text)
    text = repeater.processor(text)
    text = currency.processor(text)
    text = cardinals.processor(text)
    text = decimals.processor(text)
    text = ordinals.processor(text)
    text = punctuations.processor(text)
    text = dict_verbalize(text)
    text = text.replace("៘", "ល៉ៈ")
    text = text.replace("…", " ")
    text = text.replace("•", " ")
    text = re.sub(r"\s+", " ", text.strip())
    
    return text

def asr_normalize(text: str) -> str:
    text = normalize.processor(text)
    text = phone_numbers.processor(text, chunk_size=3)
    text = datetime.date_processor(text)
    text = datetime.time_processor(text)
    text = urls.processor(text)
    text = repeater.processor(text)
    text = currency.processor(text)
    text = cardinals.processor(text)
    text = decimals.processor(text)
    text = ordinals.processor(text)
    text = punctuations.processor(text)
    text = dict_verbalize(text)
    text = re.sub(r"\s+", " ", text.strip())
    
    return text



__all__ = [
  "ascii_lines",
  "cardinals",
  "dictionary",
  "currency",
  "datetime",
  "decimals",
  "hashtags",
  "license_plate",
  "normalize",
  "ordinals",
  "parenthesis",
  "phone_numbers",
  "punctuations",
  "repeater",
  "urls",
  "quotings",
  "dict_verbalize",
  "tts_normalize",
  "asr_normalize"
]
