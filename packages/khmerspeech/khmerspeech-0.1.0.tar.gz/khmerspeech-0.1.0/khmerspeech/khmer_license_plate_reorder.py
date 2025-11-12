import regex as re

RE_PLATE_NUMBER = re.compile(r"([0-9០-៩]+[A-Z]+)[\- ]([0-9០-៩]{4,})")
RE_PLATE_SQUARE_NUMBER = re.compile(r"([0-9០-៩])\1{3}")


def _replacer(m):
  left = " ".join(m[1])
  right = (
    f"ការ៉េ{m[2][0]}"
    if RE_PLATE_SQUARE_NUMBER.search(m[2])
    else m[2][:2] + "▁" + m[2][2:]
  )
  return f"{left} {right}"


def license_plate_reorder(text):
  return RE_PLATE_NUMBER.sub(_replacer, text)
