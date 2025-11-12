# import regex as re
# from phonenumbers import PhoneNumberMatcher

# RE_NON_NUMBER = re.compile(r"[^\d+]+")

# def overwrite_spans(text, replacements):
#   replacements.sort(reverse=True)
#   for start, end, replacement in replacements:
#     start = max(start, 0)
#     end = min(end, len(text))
#     text = text[:start] + replacement + text[end:]
#   return text

# def processor(text: str, chunk_size=2, delimiter="▁", country_code="KH") -> str:
#   replacements = []
#   for m in PhoneNumberMatcher(text, country_code):
#     phone_number = str(m.number.national_number)
#     carrier_code = phone_number[:2]
#     phone_number_id = phone_number[2:]
#     i = 0
#     chunks = []
#     while i < len(phone_number_id):
#       c = phone_number_id[i : i + chunk_size]
#       if len(c) == chunk_size:
#         chunks.append(c)
#       else:
#         chunks[-1] += c
#       i += chunk_size
#     digits = []
#     for chunk in chunks:
#       for i, c in enumerate(chunk):
#         digits.append(c)
#         if c != "0":
#           digits[-1] = chunk[i:]
#           break
#     normalized = delimiter.join(digits)
#     result = f"0{delimiter}{carrier_code}{delimiter}{normalized}"
#     replacements.append((m.start, m.end, result))
#   return overwrite_spans(text, replacements)

import regex as re
from phonenumbers import PhoneNumberMatcher

RE_NON_NUMBER = re.compile(r"[^\d+]+")

def overwrite_spans(text, replacements):
    replacements.sort(reverse=True)
    for start, end, replacement in replacements:
        start = max(start, 0)
        end = min(end, len(text))
        text = text[:start] + replacement + text[end:]
    return text

def processor(text: str, chunk_size=2, delimiter="▁", country_code="KH") -> str:
    replacements = []
    for m in PhoneNumberMatcher(text, country_code):
        # Get the original matched text to preserve leading zeros
        original_match = text[m.start:m.end]
        
        # Extract just the digits from the original match
        digits_only = re.sub(r'[^\d]', '', original_match)
        
        # Handle the number based on its format
        if digits_only.startswith('855'):
            # International format: +855 XX XXXXXX
            if len(digits_only) >= 11:
                carrier_code = digits_only[3:5]  # Skip +855
                phone_number_id = digits_only[5:]
            else:
                carrier_code = digits_only[3:5] if len(digits_only) > 5 else digits_only[3:]
                phone_number_id = digits_only[5:] if len(digits_only) > 5 else ""
        else:
            # National format: 0XX XXXXXX
            if len(digits_only) >= 9:
                carrier_code = digits_only[1:3]  # Skip leading 0
                phone_number_id = digits_only[3:]
            else:
                carrier_code = digits_only[1:3] if len(digits_only) > 3 else digits_only[1:]
                phone_number_id = digits_only[3:] if len(digits_only) > 3 else ""
        
        # Split the remaining number into chunks
        i = 0
        chunks = []
        while i < len(phone_number_id):
            c = phone_number_id[i : i + chunk_size]
            if len(c) == chunk_size:
                chunks.append(c)
            else:
                # If last chunk is shorter, merge with previous chunk
                if chunks:
                    chunks[-1] += c
                else:
                    chunks.append(c)
            i += chunk_size
        
        # Process chunks - handle leading zeros properly
        digits = []
        for chunk in chunks:
            # If chunk is all zeros, keep as individual digits
            if all(c == '0' for c in chunk):
                digits.extend(list(chunk))
            else:
                # Find first non-zero digit
                first_non_zero = 0
                for i, c in enumerate(chunk):
                    if c != '0':
                        first_non_zero = i
                        break
                
                # Add leading zeros individually
                for i in range(first_non_zero):
                    digits.append('0')
                
                # Add the rest as a group
                if first_non_zero < len(chunk):
                    digits.append(chunk[first_non_zero:])
        
        # Join with delimiter
        normalized = delimiter.join(digits)
        result = f"0{delimiter}{carrier_code}{delimiter}{normalized}"
        replacements.append((m.start, m.end, result))
    
    return overwrite_spans(text, replacements)