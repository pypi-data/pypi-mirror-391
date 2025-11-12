import regex as re

LINE_PATTERN = re.compile(r"^[\s\-\_=#\*\~`\/\\\|]{3,}$")
INLINE_PATTERN = re.compile(r"[\-\_=#\*\~`\/\\\|]{3,}")


def processor(text: str) -> str:
  """Remove ASCII art dividers and collapse inline rulers."""
  lines = []
  for line in text.splitlines():
    if LINE_PATTERN.match(line.strip()):
      lines.append("")
    else:
      cleaned = INLINE_PATTERN.sub("", line)
      lines.append(cleaned)
  return "\n".join(lines)


__all__ = ["processor"]
