def arabic_number(n):
    """Convert western arabic numerals to eastern arabic numerals"""
    eastern = '٠١٢٣٤٥٦٧٨٩'
    western = '0123456789'
    return eastern[western.index(str(n))] if str(n) in western else n

def arabic_letter(letter):
    """Convert English letters to their Arabic equivalents"""
    mapping = {
        'A': 'أ',
        'B': 'ب',
        'D': 'د',
        'E': 'ع',
        'G': 'ق',
        'H': 'ه',
        'J': 'ح',
        'K': 'ك',
        'L': 'ل',
        'N': 'ن',
        'R': 'ر',
        'S': 'س',
        'T': 'ط',
        'U': 'و',
        'V': 'ى',
        'X': 'ص',
        'Z': 'م'
    }
    return mapping.get(letter.upper(), letter)

def english_letter(letter):
    """Convert Arabic letters to their English equivalents"""
    mapping = {
        'أ': 'A',
        'ب': 'B',
        'د': 'D',
        'ع': 'E',
        'ق': 'G',
        'ه': 'H',
        'ح': 'J',
        'ك': 'K',
        'ل': 'L',
        'ن': 'N',
        'ر': 'R',
        'س': 'S',
        'ط': 'T',
        'و': 'U',
        'ى': 'V',
        'ص': 'X',
        'م': 'Z'
    }
    return mapping.get(letter, letter) 