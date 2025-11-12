import regex as re

try:
  import khmercut
except ImportError:  # pragma: no cover - optional dependency
  khmercut = None


def _override(text, start, end, replacement):
  chunk_start = text[0:start]
  chunk_end = text[end:]
  text = chunk_start + replacement + chunk_end
  return text


def _extended_word_tokenize(text, tokenizer=None):
  items = []
  for m in re.finditer(r"([^\u1780-\u17ff\s]+)|([\u1780-\u17ff\s]+)", text):
    if m.group(1):
      items.append(m.group(1))
      continue

    if tokenizer is not None:
      tokens = tokenizer(m.group(2))
    elif khmercut is not None:
      tokens = khmercut.tokenize(m.group(2))
    else:
      tokens = m.group(2).split()
    for item in tokens:
      whitelisted_items = ["ឯទៀត"]
      skipped = False
      for whitelist in whitelisted_items:
        if item.endswith(whitelist):
          items.append(item[0 : len(whitelist)])
          items.append(whitelist)
          skipped = True

      if skipped:
        continue

      items.append(item)
      continue

  return items


def repeaters_verbalize(text, sep="▁", tokenizer=None):
  if not re.search(r"ៗ", text):
    return text

  index_offset = 0
  cloned_text = text

  for match in re.finditer(r"ៗ+", cloned_text):
    offset_text = text[0 : match.start() + index_offset]
    tokens = _extended_word_tokenize(offset_text, tokenizer=tokenizer)
    tokens = tokens[-3:]
    replacement = None

    if len(tokens) <= 1:
      replacement = tokens[0]

    if len(tokens) > 1:
      if tokens[-2] in set(["1", "មួយ", "ទាំង", "លើក"]):
        replacement = "".join(tokens[-2:])

      if tokens[-1] in set(["ឡើង", "ទៅ", "ម្ដង", "ទៀត"]):
        if tokens[-2] in set(["ម៉ោង", "ថ្ងៃ", "ខែ", "ឆ្នាំ", "សប្ដាហ៍", "អាទិត្យ", "យប់"]):
          replacement = "".join(tokens[-3:])
        elif tokens[-2] in set(["ពេល"]):
          replacement = tokens[-1]
        else:
          replacement = "".join(tokens[-2:])

      if tokens[-2] == "ម្នាក់" and tokens[-1] == "ម្ដង":
        replacement = "".join(tokens[-2:])

      if tokens[-1] == "ម្នាក់" and tokens[-2] == "ម្ដង":
        replacement = "".join(tokens[-2:])

    # fallback to one word
    if replacement is None:
      replacement = tokens[-1]

    text = _override(
      text,
      match.start() + index_offset,
      match.end() + index_offset,
      f"{sep}{replacement}",
    )

    index_offset += len(replacement) - (match.end() - match.start()) + 1
  return text


if __name__ == "__main__":
  print(repeaters_verbalize("បន្តិចម្ដងៗ", sep="+"))
