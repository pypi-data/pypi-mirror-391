"""
Unicode ranges and utility functions for character range checking.

This module provides easy access to Unicode script ranges and character categories,
as well as utility functions for checking if characters belong to specific ranges.
"""

from .script_ranges import SCRIPT_CORE_RANGES, SHARED_RANGES


class RangeAccessor:
    """
    Provides attribute-style access to Unicode ranges.

    This allows users to access ranges like:
    - ranges.Arab for Arabic script
    - ranges.numbers for number characters
    - ranges.punctuation for punctuation characters
    """

    def __init__(self, ranges_dict, range_type="script"):
        self._ranges = ranges_dict
        self._range_type = range_type

    def __getattr__(self, name):
        if name in self._ranges:
            return self._ranges[name]
        raise AttributeError(
            f"'{self._range_type}' ranges has no attribute '{name}'. "
            f"Available ranges: {', '.join(sorted(self._ranges.keys()))}"
        )

    def __dir__(self):
        return sorted(self._ranges.keys())

    def __repr__(self):
        available = ", ".join(sorted(self._ranges.keys()))
        return f"<{self._range_type.title()}Ranges: {available}>"


# Create convenient access objects
scripts = RangeAccessor(SCRIPT_CORE_RANGES, "script")
categories = RangeAccessor(SHARED_RANGES, "category")


def in_range(character, *ranges):
    """
    Check if a character is in one or more Unicode ranges.

    This function can check if a character belongs to any of the specified ranges.
    It works with both script ranges (e.g., ranges.Arab) and category ranges
    (e.g., ranges.numbers), and can accept multiple ranges to check if a character
    is in range A OR range B OR range C...

    Args:
        character (str): A single character to check
        *ranges: One or more range lists. Each range is a list of (start, end) tuples.
                Can be script ranges like ranges.Arab or category ranges like ranges.numbers.

    Returns:
        bool: True if the character is in any of the specified ranges, False otherwise.

    Raises:
        ValueError: If character is not a single character
        ValueError: If no ranges are provided

    Example:
        >>> from unscript import ranges, in_range

        # Check if character is Arabic
        >>> in_range('ا', ranges.Arab)
        True

        # Check if character is a digit
        >>> in_range('5', ranges.numbers)
        True

        # Check if character is Arabic OR a number
        >>> in_range('5', ranges.Arab, ranges.numbers)
        True
        >>> in_range('ا', ranges.Arab, ranges.numbers)
        True
        >>> in_range('A', ranges.Arab, ranges.numbers)
        False

        # Check if character is Latin OR punctuation
        >>> in_range('!', ranges.Latn, ranges.punctuation)
        True
        >>> in_range('A', ranges.Latn, ranges.punctuation)
        True

        # Works with script and category ranges together
        >>> in_range('。', ranges.Hans, ranges.punctuation)  # CJK punctuation
        True
    """
    # Validate input
    if not isinstance(character, str) or len(character) != 1:
        raise ValueError("character must be a single character string")

    if not ranges:
        raise ValueError("At least one range must be provided")

    # Get character code point
    char_code = ord(character)

    # Check if character is in any of the provided ranges
    for range_list in ranges:
        if not isinstance(range_list, list):
            raise ValueError("Each range must be a list of (start, end) tuples")

        for start, end in range_list:
            if start <= char_code <= end:
                return True

    return False


def list_scripts():
    """
    Get a list of all available script names.

    Returns:
        list: Sorted list of available script codes

    Example:
        >>> from unscript import ranges
        >>> scripts = ranges.list_scripts()
        >>> 'Arab' in scripts
        True
    """
    return sorted(SCRIPT_CORE_RANGES.keys())


def list_categories():
    """
    Get a list of all available category names.

    Returns:
        list: Sorted list of available category names

    Example:
        >>> from unscript import ranges
        >>> categories = ranges.list_categories()
        >>> 'numbers' in categories
        True
    """
    return sorted(SHARED_RANGES.keys())


def get_range_info(range_name):
    """
    Get information about a specific range.

    Args:
        range_name (str): Name of the script or category

    Returns:
        dict: Information about the range including type, name, and range count

    Example:
        >>> from unscript import ranges
        >>> info = ranges.get_range_info('Arab')
        >>> info['type']
        'script'
        >>> info['range_count'] > 0
        True
    """
    if range_name in SCRIPT_CORE_RANGES:
        return {
            "type": "script",
            "name": range_name,
            "ranges": SCRIPT_CORE_RANGES[range_name],
            "range_count": len(SCRIPT_CORE_RANGES[range_name]),
        }
    elif range_name in SHARED_RANGES:
        return {
            "type": "category",
            "name": range_name,
            "ranges": SHARED_RANGES[range_name],
            "range_count": len(SHARED_RANGES[range_name]),
        }
    else:
        raise ValueError(
            f"Unknown range '{range_name}'. Available: {', '.join(sorted(list(SCRIPT_CORE_RANGES.keys()) + list(SHARED_RANGES.keys())))}"
        )


# For backward compatibility and convenience, also expose ranges directly
# This allows both ranges.Arab and ranges.scripts.Arab to work
def __getattr__(name):
    """Allow direct access to ranges via ranges.Arab syntax."""
    if name in SCRIPT_CORE_RANGES:
        return SCRIPT_CORE_RANGES[name]
    elif name in SHARED_RANGES:
        return SHARED_RANGES[name]
    else:
        available = sorted(list(SCRIPT_CORE_RANGES.keys()) + list(SHARED_RANGES.keys()))
        raise AttributeError(
            f"module 'ranges' has no attribute '{name}'. "
            f"Available ranges: {', '.join(available)}"
        )


def __dir__():
    """Return all available range names for auto-completion."""
    return sorted(
        list(SCRIPT_CORE_RANGES.keys())
        + list(SHARED_RANGES.keys())
        + [
            "scripts",
            "categories",
            "in_range",
            "list_scripts",
            "list_categories",
            "get_range_info",
        ]
    )
