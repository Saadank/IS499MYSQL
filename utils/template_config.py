from fastapi.templating import Jinja2Templates
from pathlib import Path

def arabic_numbers(number):
    """Convert English numbers to Arabic numbers"""
    if not number:
        return ""
    arabic_nums = {
        '0': '٠', '1': '١', '2': '٢', '3': '٣', '4': '٤',
        '5': '٥', '6': '٦', '7': '٧', '8': '٨', '9': '٩'
    }
    return ''.join(arabic_nums.get(c, c) for c in str(number))

def arabic_letters(letters):
    """Convert English letters to Arabic letters"""
    if not letters:
        return ""
    arabic_letters = {
        'A': 'أ', 'B': 'ب', 'C': 'س', 'D': 'د', 'E': 'ع',
        'F': 'ف', 'G': 'ج', 'H': 'ح', 'I': 'ي', 'J': 'ج',
        'K': 'ك', 'L': 'ل', 'M': 'م', 'N': 'ن', 'O': 'و',
        'P': 'ب', 'Q': 'ق', 'R': 'ر', 'S': 'س', 'T': 'ت',
        'U': 'و', 'V': 'ف', 'W': 'و', 'X': 'كس', 'Y': 'ي',
        'Z': 'ز'
    }
    return ''.join(arabic_letters.get(c.upper(), c) for c in str(letters))

# Create a single instance of Jinja2Templates
templates = Jinja2Templates(directory="templates")

# Register custom filters
templates.env.filters["arabic_numbers"] = arabic_numbers
templates.env.filters["arabic_letters"] = arabic_letters 