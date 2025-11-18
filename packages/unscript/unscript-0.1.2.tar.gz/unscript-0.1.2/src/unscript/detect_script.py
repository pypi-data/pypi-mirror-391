"""
Script detection functionality for multilingual text analysis.

This module provides the detect_script function that analyzes text and returns
the percentage distribution of different Unicode scripts found.
"""

from .script_ranges import SCRIPT_CORE_RANGES, is_char_in_script, is_char_in_category


def detect_script(text, include_categories=False, min_threshold=0.01):
    """
    Analyze text and return percentage distribution of different scripts found.

    This function examines each character in the input text and determines which
    Unicode script it belongs to, then calculates the percentage distribution.

    Args:
        text (str): The text to analyze
        include_categories (bool): Whether to include shared categories (spaces, numbers,
                                 punctuation, symbols) in the analysis. Defaults to False.
        min_threshold (float): Minimum percentage threshold to include in results.
                             Scripts below this threshold are excluded. Defaults to 0.01 (1%).

    Returns:
        dict: Dictionary mapping script codes to their percentages. When include_categories=True,
              also includes categories like 'spaces', 'numbers', etc.
              Example: {'Latn': 70.0, 'Arab': 30.0}

    Example:
        >>> detect_script("Hello World!")
        {'Latn': 100.0}

        >>> detect_script("Hello مرحبا 123!")
        {'Latn': 55.56, 'Arab': 44.44}

        >>> detect_script("Hello مرحبا 123!", include_categories=True)
        {'Latn': 41.67, 'Arab': 25.0, 'spaces': 16.67, 'punctuation': 8.33, 'numbers': 8.33}

        >>> detect_script("你好世界")
        {'Hans': 100.0}
    """
    if not isinstance(text, str) or not text:
        return {}

    # Count characters by script and category
    script_counts = {}
    category_counts = {}

    for char in text:
        char_code = ord(char)

        # Check which script this character belongs to
        found_in_script = False
        for script in SCRIPT_CORE_RANGES:
            if is_char_in_script(char_code, script):
                script_counts[script] = script_counts.get(script, 0) + 1
                found_in_script = True
                break

        # If not found in any script and we're including categories, check categories
        if not found_in_script and include_categories:
            # Check categories in order of priority: punctuation > numbers > symbols > spaces
            categories_priority = ["punctuation", "numbers", "symbols", "spaces"]

            for category in categories_priority:
                if is_char_in_category(char_code, category):
                    category_counts[category] = category_counts.get(category, 0) + 1
                    break

    # Calculate total characters for percentage calculation
    if include_categories:
        # Include all characters when categories are included
        total_chars = len(text)
    else:
        # Only count script characters when categories are excluded
        total_chars = sum(script_counts.values())

    # Return empty if no script characters found
    if total_chars == 0:
        return {}

    results = {}

    # Add script percentages
    for script, count in script_counts.items():
        percentage = (count / total_chars) * 100
        if percentage >= min_threshold:
            results[script] = round(percentage, 2)

    # Add category percentages if requested
    if include_categories:
        for category, count in category_counts.items():
            percentage = (count / total_chars) * 100
            if percentage >= min_threshold:
                results[category] = round(percentage, 2)

    return results


def detect_script_detailed(text, normalize_whitespace=False):
    """
    Provide detailed script detection analysis including character-by-character breakdown.

    Args:
        text (str): The text to analyze
        normalize_whitespace (bool): Whether to treat all whitespace as generic spaces
                                   for analysis purposes. Defaults to False.

    Returns:
        dict: Dictionary with detailed analysis including:
              - 'summary': Same as detect_script() output
              - 'total_chars': Total number of characters analyzed
              - 'breakdown': List of dicts with char, script/category, and position info
              - 'script_chars': Dict mapping scripts to character lists
              - 'category_chars': Dict mapping categories to character lists

    Example:
        >>> result = detect_script_detailed("Hi! 你好")
        >>> result['summary']
        {'Latn': 40.0, 'Hans': 40.0, 'punctuation': 20.0}
        >>> result['total_chars']
        5
        >>> len(result['breakdown'])
        5
    """
    if not isinstance(text, str):
        return {
            "summary": {},
            "total_chars": 0,
            "breakdown": [],
            "script_chars": {},
            "category_chars": {},
        }

    if normalize_whitespace:
        # Replace all whitespace with regular spaces
        import re

        text = re.sub(r"\s+", " ", text)

    breakdown = []
    script_chars = {}
    category_chars = {}
    script_counts = {}
    category_counts = {}

    for i, char in enumerate(text):
        char_code = ord(char)
        char_info = {
            "char": char,
            "position": i,
            "code_point": char_code,
            "script": None,
            "category": None,
        }

        # Check which script this character belongs to
        found_in_script = False
        for script in SCRIPT_CORE_RANGES:
            if is_char_in_script(char_code, script):
                char_info["script"] = script
                script_counts[script] = script_counts.get(script, 0) + 1
                if script not in script_chars:
                    script_chars[script] = []
                script_chars[script].append(char)
                found_in_script = True
                break

        # If not found in any script, check categories
        if not found_in_script:
            categories_priority = ["punctuation", "numbers", "symbols", "spaces"]

            for category in categories_priority:
                if is_char_in_category(char_code, category):
                    char_info["category"] = category
                    category_counts[category] = category_counts.get(category, 0) + 1
                    if category not in category_chars:
                        category_chars[category] = []
                    category_chars[category].append(char)
                    break

        breakdown.append(char_info)

    # Calculate percentages for summary
    total_chars = len(text)
    summary = {}

    if total_chars > 0:
        for script, count in script_counts.items():
            percentage = (count / total_chars) * 100
            summary[script] = round(percentage, 2)

        for category, count in category_counts.items():
            percentage = (count / total_chars) * 100
            summary[category] = round(percentage, 2)

    return {
        "summary": summary,
        "total_chars": total_chars,
        "breakdown": breakdown,
        "script_chars": script_chars,
        "category_chars": category_chars,
    }


def get_dominant_script(text, min_percentage=30.0):
    """
    Get the dominant script in the text, if any.

    Args:
        text (str): The text to analyze
        min_percentage (float): Minimum percentage required to be considered dominant.
                               Defaults to 30.0%.

    Returns:
        str or None: The dominant script code if found, None otherwise.

    Example:
        >>> get_dominant_script("Hello world! مرحبا")
        'Latn'
        >>> get_dominant_script("Hi! 你好")  # No script has >30%
        None
    """
    results = detect_script(text, include_categories=False)

    if not results:
        return None

    # Find the script with the highest percentage
    dominant_script = max(results.items(), key=lambda x: x[1])
    script_name, percentage = dominant_script

    if percentage >= min_percentage:
        return script_name

    return None


def is_script_mixed(text, threshold=10.0):
    """
    Determine if text contains a significant mix of different scripts.

    Args:
        text (str): The text to analyze
        threshold (float): Minimum percentage for a script to be considered
                          significant. Defaults to 10.0%.

    Returns:
        bool: True if text contains multiple scripts above the threshold, False otherwise.

    Example:
        >>> is_script_mixed("Hello مرحبا")
        True
        >>> is_script_mixed("Hello world!")
        False
    """
    results = detect_script(text, include_categories=False)

    # Count scripts that meet the threshold
    significant_scripts = sum(
        1 for percentage in results.values() if percentage >= threshold
    )

    return significant_scripts > 1
