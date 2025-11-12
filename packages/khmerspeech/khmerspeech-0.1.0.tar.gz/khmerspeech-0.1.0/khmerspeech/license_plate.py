from .khmer_license_plate_reorder import license_plate_reorder


def processor(text: str) -> str:
  """Normalize Cambodian license plate spacing."""
  return license_plate_reorder(text)


__all__ = ["processor"]
