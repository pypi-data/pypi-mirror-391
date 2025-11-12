import csv
from pathlib import Path

import regex as re


def file_dict(names):
  m = {}
  base_dir = Path(__file__).with_name("dict")
  for name in names:
    with open(base_dir / name, encoding="utf-8") as infile:
      reader = csv.reader(infile, delimiter="\t")
      for k, v in reader:
        m[k] = v
        m[k.lower()] = v
  return m


spellings_dict = file_dict(["spellings.tsv"])
verbatim_dict = file_dict(["verbatim.tsv"])
verbatim_trans = str.maketrans(verbatim_dict)
abbr_dict = file_dict(
  ["abbreviations_unit.tsv", "computer_measure_unit.tsv", "measure_unit.tsv"]
)

RE_COMMON_UNITS = re.compile(
  rf"([\d\u17e0-\u17e9]([\d\u17e0-\u17e9,\.]+)?[ ]*)({'|'.join(abbr_dict.keys())})([ ]|$)"
)


def _common_unit_replacer(m):
  return f"{m[1]}▁{abbr_dict.get(m[3])} "


def dictionary_verbalize(text: str) -> str:
  text = RE_COMMON_UNITS.sub(_common_unit_replacer, text)
  text = text.translate(verbatim_trans)
  for k, v in spellings_dict.items():
    text = text.replace(k, v)
  return text
