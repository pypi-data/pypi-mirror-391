"""
Unicode script ranges for character detection and filtering.

This module contains the core character ranges for each supported Unicode script
and shared character ranges for optional inclusion (spaces, numbers, punctuation, symbols).
"""

# Define character ranges for each script (core ranges only)
SCRIPT_CORE_RANGES = {
    "Latn": [
        (0x0041, 0x005A),  # Latin uppercase
        (0x0061, 0x007A),  # Latin lowercase
        (0x00C0, 0x00FF),  # Latin-1 Supplement (excluding symbols)
        (0x0100, 0x017F),  # Latin Extended-A
        (0x0180, 0x024F),  # Latin Extended-B
        (0x1E00, 0x1EFF),  # Latin Extended Additional
    ],
    "Arab": [
        (0x0600, 0x06FF),  # Arabic
        (0x0750, 0x077F),  # Arabic Supplement
        (0x08A0, 0x08FF),  # Arabic Extended-A
        (0xFB50, 0xFDFF),  # Arabic Presentation Forms-A
        (0xFE70, 0xFEFF),  # Arabic Presentation Forms-B
    ],
    "Hebr": [
        (0x0590, 0x05FF),  # Hebrew
        (0xFB1D, 0xFB4F),  # Hebrew Presentation Forms
    ],
    "Thai": [
        (0x0E00, 0x0E7F),  # Thai
    ],
    "Khmr": [
        (0x1780, 0x17FF),  # Khmer
        (0x19E0, 0x19FF),  # Khmer Symbols
    ],
    "Hang": [
        (0xAC00, 0xD7AF),  # Hangul Syllables
        (0x1100, 0x11FF),  # Hangul Jamo
        (0x3130, 0x318F),  # Hangul Compatibility Jamo
        (0xA960, 0xA97F),  # Hangul Jamo Extended-A
        (0xD7B0, 0xD7FF),  # Hangul Jamo Extended-B
    ],
    "Hans": [
        (0x4E00, 0x9FFF),  # CJK Unified Ideographs
        (0x3400, 0x4DBF),  # CJK Unified Ideographs Extension A
        (0x20000, 0x2A6DF),  # CJK Unified Ideographs Extension B
        (0x2A700, 0x2B73F),  # CJK Unified Ideographs Extension C
        (0x2B740, 0x2B81F),  # CJK Unified Ideographs Extension D
        (0x2B820, 0x2CEAF),  # CJK Unified Ideographs Extension E
        (0x2CEB0, 0x2EBEF),  # CJK Unified Ideographs Extension F
        (0x3000, 0x303F),  # CJK Symbols and Punctuation
        (0x31C0, 0x31EF),  # CJK Strokes
        (0xFE30, 0xFE4F),  # CJK Compatibility Forms
        (0xFF00, 0xFFEF),  # Halfwidth and Fullwidth Forms
    ],
    "Jpan": [
        (0x3040, 0x309F),  # Hiragana
        (0x30A0, 0x30FF),  # Katakana
        (0x31F0, 0x31FF),  # Katakana Phonetic Extensions
        (0x4E00, 0x9FFF),  # CJK Unified Ideographs
        (0x3400, 0x4DBF),  # CJK Unified Ideographs Extension A
        (0x20000, 0x2A6DF),  # CJK Unified Ideographs Extension B
        (0x2A700, 0x2B73F),  # CJK Unified Ideographs Extension C
        (0x2B740, 0x2B81F),  # CJK Unified Ideographs Extension D
        (0x3000, 0x303F),  # CJK Symbols and Punctuation
        (0x31C0, 0x31EF),  # CJK Strokes
        (0xFF00, 0xFFEF),  # Halfwidth and Fullwidth Forms
        (0x1B000, 0x1B0FF),  # Kana Supplement
        (0x1B100, 0x1B12F),  # Kana Extended-A
        (0x1B130, 0x1B16F),  # Small Kana Extension
    ],
    "Cyrl": [
        (0x0400, 0x04FF),  # Cyrillic
        (0x0500, 0x052F),  # Cyrillic Supplement
        (0x2DE0, 0x2DFF),  # Cyrillic Extended-A
        (0xA640, 0xA69F),  # Cyrillic Extended-B
    ],
    "Geor": [
        (0x10A0, 0x10FF),  # Georgian
        (0x2D00, 0x2D2F),  # Georgian Supplement
    ],
    "Deva": [
        (0x0900, 0x097F),  # Devanagari
        (0xA8E0, 0xA8FF),  # Devanagari Extended
    ],
    "Beng": [
        (0x0980, 0x09FF),  # Bengali
    ],
    "Gujr": [
        (0x0A80, 0x0AFF),  # Gujarati
    ],
    "Guru": [
        (0x0A00, 0x0A7F),  # Gurmukhi
    ],
    "Ethi": [
        (0x1200, 0x137F),  # Ethiopic
        (0x1380, 0x139F),  # Ethiopic Supplement
        (0x2D80, 0x2DDF),  # Ethiopic Extended
        (0xAB00, 0xAB2F),  # Ethiopic Extended-A
    ],
    "Grek": [
        (0x0370, 0x03FF),  # Greek and Coptic
        (0x1F00, 0x1FFF),  # Greek Extended
    ],
    "Taml": [
        (0x0B80, 0x0BFF),  # Tamil
    ],
    "Mlym": [
        (0x0D00, 0x0D7F),  # Malayalam
    ],
    "Telu": [
        (0x0C00, 0x0C7F),  # Telugu
    ],
    "Knda": [
        (0x0C80, 0x0CFF),  # Kannada
    ],
    "Orya": [
        (0x0B00, 0x0B7F),  # Oriya
    ],
    "Sinh": [
        (0x0D80, 0x0DFF),  # Sinhala
    ],
    "Mymr": [
        (0x1000, 0x109F),  # Myanmar
        (0xA9E0, 0xA9FF),  # Myanmar Extended-B
        (0xAA60, 0xAA7F),  # Myanmar Extended-A
    ],
    "Laoo": [
        (0x0E80, 0x0EFF),  # Lao
    ],
    "Tibt": [
        (0x0F00, 0x0FFF),  # Tibetan
    ],
    "Armn": [
        (0x0530, 0x058F),  # Armenian
    ],
    "Thaa": [
        (0x0780, 0x07BF),  # Thaana
    ],
    "Mong": [
        (0x1800, 0x18AF),  # Mongolian
    ],
    "Viet": [
        (0x1E00, 0x1EFF),  # Latin Extended Additional (Vietnamese)
    ],
    "Brai": [
        (0x2800, 0x28FF),  # Braille Patterns
    ],
    "Tfng": [
        (0x2D30, 0x2D7F),  # Tifinagh
    ],
    "Hant": [
        (0x4E00, 0x9FFF),  # CJK Unified Ideographs
        (0x3400, 0x4DBF),  # CJK Unified Ideographs Extension A
        (0x20000, 0x2A6DF),  # CJK Unified Ideographs Extension B
        (0x2A700, 0x2B73F),  # CJK Unified Ideographs Extension C
        (0x2B740, 0x2B81F),  # CJK Unified Ideographs Extension D
        (0x2B820, 0x2CEAF),  # CJK Unified Ideographs Extension E
        (0x2CEB0, 0x2EBEF),  # CJK Unified Ideographs Extension F
        (0x3000, 0x303F),  # CJK Symbols and Punctuation
        (0x31C0, 0x31EF),  # CJK Strokes
        (0xFE30, 0xFE4F),  # CJK Compatibility Forms
        (0xFF00, 0xFFEF),  # Halfwidth and Fullwidth Forms
        (0x2F00, 0x2FDF),  # Kangxi Radicals
        (0x2E80, 0x2EFF),  # CJK Radicals Supplement
        (0xF900, 0xFAFF),  # CJK Compatibility Ideographs
        (0x2F800, 0x2FA1F),  # CJK Compatibility Ideographs Supplement
    ],
    "Cans": [
        (0x1400, 0x167F),  # Unified Canadian Aboriginal Syllabics
        (0x18B0, 0x18FF),  # Unified Canadian Aboriginal Syllabics Extended
    ],
    "Cher": [
        (0x13A0, 0x13FF),  # Cherokee
        (0xAB70, 0xABBF),  # Cherokee Supplement
    ],
    "Goth": [
        (0x10330, 0x1034F),  # Gothic
    ],
    "Olck": [
        (0x1C50, 0x1C7F),  # Ol Chiki
    ],
    "Mtei": [
        (0xAAE0, 0xAAFF),  # Meetei Mayek Extensions
        (0xABC0, 0xABFF),  # Meetei Mayek
    ],
    "Syrc": [
        (0x0700, 0x074F),  # Syriac
        (0x0860, 0x086F),  # Syriac Supplement
    ],
    "Sylo": [
        (0xA800, 0xA82F),  # Syloti Nagri
    ],
    "Tale": [
        (0x1950, 0x197F),  # Tai Le
    ],
    "Yiii": [
        (0xA000, 0xA48F),  # Yi Syllables
        (0xA490, 0xA4CF),  # Yi Radicals
    ],
}


# Define punctuation subsets for level-based inclusion

# ASCII punctuation (basic): keep sentence/word punctuation and quotes, excluding brackets and special symbols
PUNCTUATION_ASCII = [
    (0x0021, 0x0021),  # !
    (0x0022, 0x0022),  # "
    (0x0027, 0x0027),  # '
    (0x002C, 0x002C),  # ,
    (0x002E, 0x002E),  # .
    (0x003A, 0x003B),  # : ;
    (0x003F, 0x003F),  # ?
]

# EXTENDED: ASCII + curly quotes + guillemets + script-specific marks + fullwidth punctuation + all brackets (ASCII + fullwidth)
PUNCTUATION_EXTENDED = (
    PUNCTUATION_ASCII
    + [
        (0x2018, 0x201F),  # curly quotes
        (0x2039, 0x203A),  # single guillemets
        (0x00AB, 0x00AB),  # «
        (0x00BB, 0x00BB),  # »
        (0x060C, 0x060C),  # Arabic comma
        (0x061B, 0x061B),  # Arabic semicolon
        (0x061F, 0x061F),  # Arabic question mark
        (0x06D4, 0x06D4),  # Arabic full stop
        (0x0964, 0x0965),  # Devanagari danda
        (0x0F0D, 0x0F0D),  # Tibetan shad
        (0x104B, 0x104B),  # Myanmar little section
        (0x17D4, 0x17D4),  # Khmer sign khan
        (0x3002, 0x3002),  # CJK ideographic full stop
        (0xFF01, 0xFF01),  # Fullwidth !
        (0xFF0C, 0xFF0C),  # Fullwidth ,
        (0xFF0E, 0xFF0E),  # Fullwidth .
        (0xFF1A, 0xFF1B),  # Fullwidth : ;
        (0xFF1F, 0xFF1F),  # Fullwidth ?
        # Brackets ASCII + fullwidth
        (0x0028, 0x0029),  # ()
        (0x005B, 0x005D),  # []
        (0x007B, 0x007D),  # {}
        (0x003C, 0x003C),  # <
        (0x003E, 0x003E),  # >
        (0xFF08, 0xFF09),  # Fullwidth ()
        (0xFF3B, 0xFF3D),  # Fullwidth []
        (0xFF5B, 0xFF5D),  # Fullwidth {}
        (0xFF1C, 0xFF1E),  # Fullwidth < = >
    ]
)

# ALL: EXTENDED + remaining general punctuation (excluding whitespace/bidi controls already treated under spaces)
PUNCTUATION_ALL = (
    PUNCTUATION_EXTENDED
    + [
        (0x2000, 0x2025),  # General Punctuation (excluding ellipsis)
        (0x2027, 0x206F),  # General Punctuation (excluding ellipsis)
        (0xFE10, 0xFE1F),  # Vertical Forms
        (0xFE30, 0xFE4F),  # CJK Compatibility Forms
        (0xFE50, 0xFE52),  # Small comma, period, semicolon
        (0xFE54, 0xFE57),  # Small colon, question mark, exclamation mark
        (0xFE58, 0xFE6F),  # Small form variants (more punctuation-like)
    ]
)

# Shared ranges that can be optionally included
SHARED_RANGES = {
    "spaces": [
        (0x0020, 0x0020),  # Space
        (0x00A0, 0x00A0),  # Non-breaking space
        (0x200B, 0x200F),  # Zero-width spaces
        (0x202F, 0x202F),  # Narrow no-break space
        (0x205F, 0x205F),  # Medium mathematical space
        (0x2066, 0x2069),  # Left-to-right isolate
        (0x206F, 0x206F),  # Right-to-left isolate
        (0x000A, 0x000A),  # New line
        (0x000D, 0x000D),  # Carriage return
        (0x0085, 0x0085),  # Next line
        (0x2028, 0x2029),  # Line separator
        (0x202F, 0x202F),  # Narrow no-break space
    ],
    "numbers": [
        (0x0030, 0x0039),  # 0-9 digits (ASCII)
        (0x0660, 0x0669),  # Arabic-Indic digits
        (0x06F0, 0x06F9),  # Extended Arabic-Indic digits
        (0x07C0, 0x07C9),  # NKo digits
        (0x0966, 0x096F),  # Devanagari digits
        (0x09E6, 0x09EF),  # Bengali digits
        (0x0A66, 0x0A6F),  # Gurmukhi digits
        (0x0AE6, 0x0AEF),  # Gujarati digits
        (0x0B66, 0x0B6F),  # Oriya digits
        (0x0BE6, 0x0BEF),  # Tamil digits
        (0x0C66, 0x0C6F),  # Telugu digits
        (0x0CE6, 0x0CEF),  # Kannada digits
        (0x0D66, 0x0D6F),  # Malayalam digits
        (0x0DE6, 0x0DEF),  # Sinhala Lith digits
        (0x0E50, 0x0E59),  # Thai digits
        (0x0ED0, 0x0ED9),  # Lao digits
        (0x0F20, 0x0F29),  # Tibetan digits
        (0x1040, 0x1049),  # Myanmar digits
        (0x1090, 0x1099),  # Myanmar Shan digits
        (0x17E0, 0x17E9),  # Khmer digits
        (0x1810, 0x1819),  # Mongolian digits
        (0x1946, 0x194F),  # Limbu digits
        (0x19D0, 0x19D9),  # New Tai Lue digits
        (0x1A80, 0x1A89),  # Tai Tham Hora digits
        (0x1A90, 0x1A99),  # Tai Tham Tham digits
        (0x1B50, 0x1B59),  # Balinese digits
        (0x1BB0, 0x1BB9),  # Sundanese digits
        (0x1C40, 0x1C49),  # Lepcha digits
        (0x1C50, 0x1C59),  # Ol Chiki digits
        (0xA620, 0xA629),  # Vai digits
        (0xA8D0, 0xA8D9),  # Saurashtra digits
        (0xA900, 0xA909),  # Kayah Li digits
        (0xA9D0, 0xA9D9),  # Javanese digits
        (0xA9F0, 0xA9F9),  # Myanmar Tai Laing digits
        (0xAA50, 0xAA59),  # Cham digits
        (0xABF0, 0xABF9),  # Meetei Mayek digits
        (0xFF10, 0xFF19),  # Fullwidth digits
    ],
    "punctuation": [
        (0x0021, 0x0021),  # ! (exclamation mark)
        (0x0022, 0x0022),  # " (quotation mark)
        (0x002C, 0x002C),  # , (comma)
        (0x002E, 0x002E),  # . (period)
        (0x003A, 0x003B),  # : and ; (colon and semicolon)
        (0x003F, 0x003F),  # ? (question mark)
        (0x0027, 0x0027),  # ' (apostrophe)
        (0x0028, 0x0029),  # ( ) (round brackets)
        (0x005B, 0x005D),  # [ ] (square brackets)
        (0x007B, 0x007D),  # { } (curly brackets)
        (0x003C, 0x003C),  # < (angle bracket)
        (0x003E, 0x003E),  # > (angle bracket)
        (0x00A1, 0x00A1),  # ¡ (inverted exclamation mark)
        (0x00BF, 0x00BF),  # ¿ (inverted question mark)
        (0x00AB, 0x00AB),  # « (left-pointing double angle quotation mark)
        (0x00BB, 0x00BB),  # » (right-pointing double angle quotation mark)
        (0x060C, 0x060C),  # ، (Arabic comma)
        (0x061B, 0x061B),  # ؛ (Arabic semicolon)
        (0x061F, 0x061F),  # ؟ (Arabic question mark)
        (0x06D4, 0x06D4),  # ۔ (Arabic full stop)
        (0x0964, 0x0965),  # । ॥ (Devanagari danda and double danda)
        (0x0F0D, 0x0F0D),  # ། (Tibetan mark shad)
        (0x104B, 0x104B),  # ။ (Myanmar sign little section)
        (0x17D4, 0x17D4),  # ។ (Khmer sign khan)
        (0x3002, 0x3002),  # 。 (CJK ideographic full stop)
        (0x2026, 0x2026),  # … (ellipsis)
        (0x2018, 0x201F),  # ‘ ’ ‚ ‛ “ ” „ ‟ (curly single/double quotes)
        (0x2039, 0x203A),  # ‹ › (single guillemets)
        (0x2000, 0x2025),  # General Punctuation (excluding ellipsis)
        (0x2027, 0x206F),  # General Punctuation (excluding ellipsis)
        (0xFE10, 0xFE1F),  # Vertical Forms
        (0xFE30, 0xFE4F),  # CJK Compatibility Forms (punctuation-related)
        (0xFE50, 0xFE52),  # Small comma, period, semicolon
        (0xFE54, 0xFE57),  # Small colon, question mark, exclamation mark
        (0xFF01, 0xFF01),  # Fullwidth exclamation mark
        (0xFF0C, 0xFF0C),  # Fullwidth comma
        (0xFF0E, 0xFF0E),  # Fullwidth period
        (0xFF1A, 0xFF1B),  # Fullwidth colon and semicolon
        (0xFF1F, 0xFF1F),  # Fullwidth question mark
        (0xFF08, 0xFF09),  # Fullwidth ( )
        (0xFF3B, 0xFF3D),  # Fullwidth [ ]
        (0xFF5B, 0xFF5D),  # Fullwidth { }
        (0xFF1C, 0xFF1C),  # Fullwidth <
        (0xFF1E, 0xFF1E),  # Fullwidth >
    ],
    "symbols": [
        (0x0023, 0x0026),  # # $ % &
        (0x002A, 0x002B),  # * +
        (0x002D, 0x002D),  # - (minus)
        (0x002F, 0x002F),  # / (slash)
        (0x003C, 0x003E),  # < = > (comparison operators)
        (0x0040, 0x0040),  # @ (at sign)
        (0x005B, 0x0060),  # [ \ ] ^ _ ` (brackets and other symbols)
        (0x007B, 0x007E),  # { | } ~ (braces and other symbols)
        (0x00A2, 0x00A5),  # Cent, pound, currency, yen signs
        (0x00B0, 0x00B0),  # Degree sign
        (0x00B1, 0x00B1),  # Plus-minus sign
        (0x00D7, 0x00D7),  # Multiplication sign
        (0x00F7, 0x00F7),  # Division sign
        (0x058F, 0x058F),  # Armenian dram
        (0x060B, 0x060B),  # Afghani sign
        (0x09F2, 0x09F3),  # Bengali rupee marks
        (0x0AF1, 0x0AF1),  # Gujarati rupee sign
        (0x0BF9, 0x0BF9),  # Tamil rupee sign
        (0x0E3F, 0x0E3F),  # Thai baht
        (0x17DB, 0x17DB),  # Khmer riel
        (0x2000, 0x2025),  # General Punctuation (excluding ellipsis)
        (0x2027, 0x206F),  # General Punctuation (excluding ellipsis)
        (0x2070, 0x209F),  # Superscripts and Subscripts
        (0x20A0, 0x20CF),  # Currency Symbols block
        (0x2100, 0x214F),  # Letterlike Symbols
        (0x2150, 0x218F),  # Number Forms
        (0x2190, 0x21FF),  # Arrows
        (0x2200, 0x22FF),  # Mathematical Operators
        (0x2300, 0x23FF),  # Miscellaneous Technical
        (0x2400, 0x243F),  # Control Pictures
        (0x2440, 0x245F),  # Optical Character Recognition
        (0x2460, 0x24FF),  # Enclosed Alphanumerics
        (0x2500, 0x257F),  # Box Drawing
        (0x2580, 0x259F),  # Block Elements
        (0x25A0, 0x25FF),  # Geometric Shapes
        (0x2600, 0x26FF),  # Miscellaneous Symbols
        (0x2700, 0x27BF),  # Dingbats
        (0x27C0, 0x27EF),  # Miscellaneous Mathematical Symbols-A
        (0x27F0, 0x27FF),  # Supplemental Arrows-A
        (0x2900, 0x297F),  # Supplemental Arrows-B
        (0x2980, 0x29FF),  # Miscellaneous Mathematical Symbols-B
        (0x2A00, 0x2AFF),  # Supplemental Mathematical Operators
        (0x2B00, 0x2BFF),  # Miscellaneous Symbols and Arrows
        (0x3000, 0x303F),  # CJK Symbols and Punctuation
        (0xFDFC, 0xFDFC),  # Rial sign
        (0xFE10, 0xFE1F),  # Vertical Forms
        (0xFE30, 0xFE4F),  # CJK Compatibility Forms
        (0xFE53, 0xFE53),  # Small question mark
        (0xFE58, 0xFE6F),  # Small form variants (excluding basic punctuation)
        (0xFE69, 0xFE69),  # Small dollar sign
        (0xFF02, 0xFF0B),  # Fullwidth symbols
        (0xFF0D, 0xFF0D),  # Fullwidth minus
        (0xFF0F, 0xFF0F),  # Fullwidth slash
        (0xFF1C, 0xFF1E),  # Fullwidth comparison operators
        (0xFF20, 0xFF20),  # Fullwidth at sign
        (0xFF3B, 0xFF40),  # Fullwidth brackets and other symbols
        (0xFF5B, 0xFF65),  # Fullwidth braces and other symbols
        (0xFFE0, 0xFFE6),  # Fullwidth cent, pound, etc.
    ],
}


def initialize_shared_ranges():
    """
    Initialize SHARED_RANGES by adding uncovered Unicode points to symbols.
    This function should be called once when the module is first imported.
    """
    # Add uncovered ranges to symbols
    covered_points = set()
    for ranges in SCRIPT_CORE_RANGES.values():
        for start, end in ranges:
            covered_points.update(range(start, end + 1))
    for ranges in SHARED_RANGES.values():
        for start, end in ranges:
            covered_points.update(range(start, end + 1))

    uncovered = []
    start = None
    for point in range(0x0000, 0x110000):
        if point not in covered_points:
            if start is None:
                start = point
        elif start is not None:
            uncovered.append((start, point - 1))
            start = None
    if start is not None:
        uncovered.append((start, 0x10FFFF))

    SHARED_RANGES["symbols"].extend(uncovered)


# Initialize the shared ranges when module is imported
initialize_shared_ranges()


def is_char_in_script(char_code, script):
    """
    Check if a character code point belongs to a specific script.

    Args:
        char_code (int): Unicode code point of the character
        script (str): Script code (e.g., 'Latn', 'Arab', 'Hans')

    Returns:
        bool: True if character belongs to the script, False otherwise
    """
    if script not in SCRIPT_CORE_RANGES:
        return False

    for start, end in SCRIPT_CORE_RANGES[script]:
        if start <= char_code <= end:
            return True
    return False


def is_char_in_category(char_code, category):
    """
    Check if a character code point belongs to a shared category.

    Args:
        char_code (int): Unicode code point of the character
        category (str): Category name ('spaces', 'numbers', 'punctuation', 'symbols')

    Returns:
        bool: True if character belongs to the category, False otherwise
    """
    if category not in SHARED_RANGES:
        return False

    for start, end in SHARED_RANGES[category]:
        if start <= char_code <= end:
            return True
    return False


def get_supported_scripts():
    """
    Get a list of all supported script codes.

    Returns:
        list: List of supported script codes
    """
    return list(SCRIPT_CORE_RANGES.keys())


def get_supported_categories():
    """
    Get a list of all supported character categories.

    Returns:
        list: List of supported category names
    """
    return list(SHARED_RANGES.keys())
