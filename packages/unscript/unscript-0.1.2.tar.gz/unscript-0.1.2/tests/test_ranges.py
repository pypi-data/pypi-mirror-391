"""
Tests for the ranges module and in_range functionality.
"""

import pytest
from unscript import ranges, in_range


class TestRangeAccess:
    """Test range access functionality."""

    def test_script_range_access(self):
        """Test accessing script ranges."""
        # Test that Arabic ranges are accessible and non-empty
        arab_ranges = ranges.Arab
        assert isinstance(arab_ranges, list)
        assert len(arab_ranges) > 0
        assert all(isinstance(r, tuple) and len(r) == 2 for r in arab_ranges)

        # Test Latin ranges
        latin_ranges = ranges.Latn
        assert isinstance(latin_ranges, list)
        assert len(latin_ranges) > 0

        # Test Chinese ranges
        hans_ranges = ranges.Hans
        assert isinstance(hans_ranges, list)
        assert len(hans_ranges) > 0

    def test_category_range_access(self):
        """Test accessing category ranges."""
        # Test numbers
        numbers_ranges = ranges.numbers
        assert isinstance(numbers_ranges, list)
        assert len(numbers_ranges) > 0

        # Test punctuation
        punct_ranges = ranges.punctuation
        assert isinstance(punct_ranges, list)
        assert len(punct_ranges) > 0

        # Test spaces
        spaces_ranges = ranges.spaces
        assert isinstance(spaces_ranges, list)
        assert len(spaces_ranges) > 0

        # Test symbols
        symbols_ranges = ranges.symbols
        assert isinstance(symbols_ranges, list)
        assert len(symbols_ranges) > 0

    def test_invalid_range_access(self):
        """Test accessing non-existent ranges."""
        with pytest.raises(AttributeError):
            _ = ranges.NonExistentScript

        with pytest.raises(AttributeError):
            _ = ranges.invalid_category

    def test_scripts_accessor(self):
        """Test the scripts accessor object."""
        # Test accessing through scripts object
        arab_ranges = ranges.scripts.Arab
        assert isinstance(arab_ranges, list)
        assert len(arab_ranges) > 0

        # Test repr
        repr_str = repr(ranges.scripts)
        assert "ScriptRanges" in repr_str
        assert "Arab" in repr_str

        # Test dir
        script_names = dir(ranges.scripts)
        assert "Arab" in script_names
        assert "Latn" in script_names
        assert "Hans" in script_names
        assert "Sylo" in script_names

    def test_categories_accessor(self):
        """Test the categories accessor object."""
        # Test accessing through categories object
        numbers_ranges = ranges.categories.numbers
        assert isinstance(numbers_ranges, list)
        assert len(numbers_ranges) > 0

        # Test repr
        repr_str = repr(ranges.categories)
        assert "CategoryRanges" in repr_str
        assert "numbers" in repr_str

        # Test dir
        category_names = dir(ranges.categories)
        assert "numbers" in category_names
        assert "punctuation" in category_names
        assert "spaces" in category_names


class TestInRangeFunction:
    """Test the in_range function."""

    def test_arabic_characters(self):
        """Test Arabic character detection."""
        # Arabic characters
        assert in_range("ا", ranges.Arab) == True  # Arabic Letter Alef
        assert in_range("ب", ranges.Arab) == True  # Arabic Letter Beh
        assert in_range("ت", ranges.Arab) == True  # Arabic Letter Teh

        # Non-Arabic characters
        assert in_range("A", ranges.Arab) == False
        assert in_range("5", ranges.Arab) == False
        assert in_range("!", ranges.Arab) == False

    def test_syloti_nagri_characters(self):
        """Test Syloti Nagri character detection (Sylo)."""
        # Syloti Nagri characters (e.g., U+A80A, U+A803)
        assert in_range("ꠊ", ranges.Sylo) == True  # U+A80A
        assert in_range("ꠃ", ranges.Sylo) == True  # U+A803
        # Non-Sylo characters
        assert in_range("A", ranges.Sylo) == False

    def test_latin_characters(self):
        """Test Latin character detection."""
        # Latin characters
        assert in_range("A", ranges.Latn) == True
        assert in_range("z", ranges.Latn) == True
        assert in_range("ñ", ranges.Latn) == True  # Latin with diacritics

        # Non-Latin characters
        assert in_range("ا", ranges.Latn) == False
        assert in_range("你", ranges.Latn) == False
        assert in_range("5", ranges.Latn) == False

    def test_chinese_characters(self):
        """Test Chinese character detection."""
        # Chinese characters
        assert in_range("你", ranges.Hans) == True
        assert in_range("好", ranges.Hans) == True
        assert in_range("世", ranges.Hans) == True

        # Non-Chinese characters
        assert in_range("A", ranges.Hans) == False
        assert in_range("ا", ranges.Hans) == False

    def test_number_characters(self):
        """Test number character detection."""
        # ASCII digits
        assert in_range("0", ranges.numbers) == True
        assert in_range("5", ranges.numbers) == True
        assert in_range("9", ranges.numbers) == True

        # Arabic-Indic digits
        assert in_range("٠", ranges.numbers) == True  # Arabic-Indic digit zero
        assert in_range("٥", ranges.numbers) == True  # Arabic-Indic digit five

        # Non-digits
        assert in_range("A", ranges.numbers) == False
        assert in_range("!", ranges.numbers) == False

    def test_punctuation_characters(self):
        """Test punctuation character detection."""
        # Common punctuation
        assert in_range("!", ranges.punctuation) == True
        assert in_range(".", ranges.punctuation) == True
        assert in_range("?", ranges.punctuation) == True
        assert in_range(",", ranges.punctuation) == True

        # Arabic punctuation
        assert in_range("؟", ranges.punctuation) == True  # Arabic question mark
        assert in_range("،", ranges.punctuation) == True  # Arabic comma

        # Non-punctuation
        assert in_range("A", ranges.punctuation) == False
        assert in_range("5", ranges.punctuation) == False

    def test_space_characters(self):
        """Test space character detection."""
        # Regular space
        assert in_range(" ", ranges.spaces) == True

        # Non-breaking space
        assert in_range("\u00a0", ranges.spaces) == True

        # Newline and carriage return
        assert in_range("\n", ranges.spaces) == True
        assert in_range("\r", ranges.spaces) == True

        # Non-space characters
        assert in_range("A", ranges.spaces) == False
        assert in_range("5", ranges.spaces) == False

    def test_multiple_ranges(self):
        """Test checking against multiple ranges."""
        # Character in first range
        assert in_range("ا", ranges.Arab, ranges.numbers) == True

        # Character in second range
        assert in_range("5", ranges.Arab, ranges.numbers) == True

        # Character in neither range
        assert in_range("A", ranges.Arab, ranges.numbers) == False

        # Character in one of many ranges
        assert in_range("!", ranges.Latn, ranges.Arab, ranges.punctuation) == True
        assert in_range("A", ranges.Latn, ranges.Arab, ranges.punctuation) == True
        assert in_range("ا", ranges.Latn, ranges.Arab, ranges.punctuation) == True

        # Character in none of many ranges
        assert in_range("你", ranges.Latn, ranges.Arab, ranges.punctuation) == False

    def test_mixed_script_and_category_ranges(self):
        """Test mixing script and category ranges."""
        # Arabic character with Arabic or number ranges
        assert in_range("ا", ranges.Arab, ranges.numbers) == True

        # Number with Arabic or number ranges
        assert in_range("5", ranges.Arab, ranges.numbers) == True

        # Latin character with Latin or punctuation ranges
        assert in_range("A", ranges.Latn, ranges.punctuation) == True

        # Punctuation with Latin or punctuation ranges
        assert in_range("!", ranges.Latn, ranges.punctuation) == True

        # Character not in any specified range
        assert in_range("你", ranges.Arab, ranges.numbers) == False

    def test_input_validation(self):
        """Test input validation for in_range function."""
        # Empty string
        with pytest.raises(ValueError, match="must be a single character"):
            in_range("", ranges.Arab)

        # Multiple characters
        with pytest.raises(ValueError, match="must be a single character"):
            in_range("AB", ranges.Arab)

        # Non-string input
        with pytest.raises(ValueError, match="must be a single character"):
            in_range(65, ranges.Arab)  # ASCII code for 'A'

        # No ranges provided
        with pytest.raises(ValueError, match="At least one range must be provided"):
            in_range("A")

        # Invalid range format
        with pytest.raises(ValueError, match="Each range must be a list"):
            in_range("A", "not_a_list")


class TestUtilityFunctions:
    """Test utility functions in ranges module."""

    def test_list_scripts(self):
        """Test list_scripts function."""
        scripts = ranges.list_scripts()
        assert isinstance(scripts, list)
        assert len(scripts) > 0
        assert "Arab" in scripts
        assert "Latn" in scripts
        assert "Hans" in scripts
        assert scripts == sorted(scripts)  # Should be sorted

    def test_list_categories(self):
        """Test list_categories function."""
        categories = ranges.list_categories()
        assert isinstance(categories, list)
        assert len(categories) > 0
        assert "numbers" in categories
        assert "punctuation" in categories
        assert "spaces" in categories
        assert "symbols" in categories
        assert categories == sorted(categories)  # Should be sorted

    def test_get_range_info_script(self):
        """Test get_range_info for scripts."""
        info = ranges.get_range_info("Arab")
        assert info["type"] == "script"
        assert info["name"] == "Arab"
        assert isinstance(info["ranges"], list)
        assert info["range_count"] > 0
        assert len(info["ranges"]) == info["range_count"]

    def test_get_range_info_category(self):
        """Test get_range_info for categories."""
        info = ranges.get_range_info("numbers")
        assert info["type"] == "category"
        assert info["name"] == "numbers"
        assert isinstance(info["ranges"], list)
        assert info["range_count"] > 0
        assert len(info["ranges"]) == info["range_count"]

    def test_get_range_info_invalid(self):
        """Test get_range_info with invalid range name."""
        with pytest.raises(ValueError, match="Unknown range"):
            ranges.get_range_info("InvalidRange")


class TestRealWorldExamples:
    """Test real-world usage examples."""

    def test_multilingual_text_checking(self):
        """Test checking characters from multilingual text."""
        text = "Hello مرحبا 你好 123 !"

        results = []
        for char in text:
            if char.isspace():
                continue

            is_latin = in_range(char, ranges.Latn)
            is_arabic = in_range(char, ranges.Arab)
            is_chinese = in_range(char, ranges.Hans)
            is_digit = in_range(char, ranges.numbers)
            is_punct = in_range(char, ranges.punctuation)

            results.append(
                {
                    "char": char,
                    "latin": is_latin,
                    "arabic": is_arabic,
                    "chinese": is_chinese,
                    "digit": is_digit,
                    "punctuation": is_punct,
                }
            )

        # Check specific characters
        h_result = next(r for r in results if r["char"] == "H")
        assert h_result["latin"] == True
        assert h_result["arabic"] == False

        arabic_result = next(r for r in results if r["char"] == "م")
        assert arabic_result["arabic"] == True
        assert arabic_result["latin"] == False

        chinese_result = next(r for r in results if r["char"] == "你")
        assert chinese_result["chinese"] == True
        assert chinese_result["latin"] == False

        digit_result = next(r for r in results if r["char"] == "1")
        assert digit_result["digit"] == True
        assert digit_result["latin"] == False

        punct_result = next(r for r in results if r["char"] == "!")
        assert punct_result["punctuation"] == True
        assert punct_result["latin"] == False

    def test_script_filtering_logic(self):
        """Test logic for filtering text by script."""
        text = "Hello123مرحبا!"

        # Keep only Latin or numbers
        latin_or_numbers = []
        for char in text:
            if in_range(char, ranges.Latn, ranges.numbers):
                latin_or_numbers.append(char)

        result = "".join(latin_or_numbers)
        assert "H" in result
        assert "e" in result
        assert "1" in result
        assert "م" not in result
        assert "!" not in result

    def test_comprehensive_range_check(self):
        """Test comprehensive range checking across all categories."""
        test_chars = {
            "A": {"expected_ranges": ["Latn"]},
            "ا": {"expected_ranges": ["Arab"]},
            "你": {"expected_ranges": ["Hans"]},
            "5": {"expected_ranges": ["numbers"]},
            "!": {"expected_ranges": ["punctuation"]},
            " ": {"expected_ranges": ["spaces"]},
            "$": {"expected_ranges": ["symbols"]},
        }

        all_script_ranges = [
            getattr(ranges, script) for script in ranges.list_scripts()
        ]
        all_category_ranges = [getattr(ranges, cat) for cat in ranges.list_categories()]

        for char, info in test_chars.items():
            # Check that character is found in expected ranges
            for expected_range in info["expected_ranges"]:
                assert in_range(
                    char, getattr(ranges, expected_range)
                ), f"Character '{char}' should be in {expected_range}"

            # Verify character is detected by at least one range
            found_in_any = in_range(char, *(all_script_ranges + all_category_ranges))
            assert (
                found_in_any
            ), f"Character '{char}' should be found in at least one range"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_ranges_handling(self):
        """Test handling of empty range lists."""
        # This shouldn't happen in practice, but test the behavior
        with pytest.raises(ValueError, match="Each range must be a list"):
            in_range("A", None)

    def test_boundary_characters(self):
        """Test characters at range boundaries."""
        # Test ASCII boundaries for Latin
        assert in_range("A", ranges.Latn) == True  # Start of uppercase
        assert in_range("Z", ranges.Latn) == True  # End of uppercase
        assert in_range("a", ranges.Latn) == True  # Start of lowercase
        assert in_range("z", ranges.Latn) == True  # End of lowercase

        # Test digit boundaries
        assert in_range("0", ranges.numbers) == True
        assert in_range("9", ranges.numbers) == True

    def test_unicode_high_codepoints(self):
        """Test characters with high Unicode code points."""
        # Test some high Unicode characters that should be in Hans ranges
        cjk_char = "\U00020000"  # First character in CJK Extension B
        if len(ranges.Hans) > 0:
            # Check if any Han ranges include this high codepoint
            found = False
            for start, end in ranges.Hans:
                if start <= ord(cjk_char) <= end:
                    found = True
                    break
            # Only assert if we expect this character to be in the ranges
            if found:
                assert in_range(cjk_char, ranges.Hans) == True
