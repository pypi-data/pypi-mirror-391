import unittest
from unscript.detect_script import (
    detect_script,
    detect_script_detailed,
    get_dominant_script,
    is_script_mixed,
)


class TestDetectScript(unittest.TestCase):

    def test_detect_script_basic_latin(self):
        """Test basic Latin script detection."""
        result = detect_script("Hello World")
        self.assertEqual(
            result, {"Latn": 100.0}
        )  # Only counting script chars, ignoring spaces

    def test_detect_script_basic_arabic(self):
        """Test basic Arabic script detection."""
        result = detect_script("مرحبا بالعالم")
        self.assertEqual(
            result, {"Arab": 100.0}
        )  # Only counting script chars, ignoring spaces

    def test_detect_script_basic_chinese(self):
        """Test basic Chinese script detection."""
        result = detect_script("你好世界")
        self.assertEqual(result, {"Hans": 100.0})

    def test_detect_script_mixed_scripts(self):
        """Test detection with mixed scripts."""
        result = detect_script("Hello مرحبا")
        self.assertIn("Latn", result)
        self.assertIn("Arab", result)
        self.assertNotIn("spaces", result)  # Default behavior excludes categories

        # Verify percentages add up to 100%
        total = sum(result.values())
        self.assertAlmostEqual(total, 100.0, places=1)

    def test_detect_script_with_numbers_default(self):
        """Test detection with numbers (default behavior excludes them)."""
        result = detect_script("Hello 123")
        self.assertEqual(result, {"Latn": 100.0})  # Numbers ignored by default

    def test_detect_script_with_punctuation_default(self):
        """Test detection with punctuation (default behavior excludes them)."""
        result = detect_script("Hello, World!")
        self.assertEqual(result, {"Latn": 100.0})  # Punctuation ignored by default

    def test_detect_script_include_categories(self):
        """Test detection with categories explicitly included."""
        result = detect_script("Hello 123", include_categories=True)
        self.assertIn("Latn", result)
        self.assertIn("numbers", result)
        self.assertIn("spaces", result)

        # Check specific percentages
        self.assertEqual(result["Latn"], 55.56)  # 5 out of 9 chars
        self.assertEqual(result["numbers"], 33.33)  # 3 out of 9 chars
        self.assertEqual(result["spaces"], 11.11)  # 1 out of 9 chars

    def test_detect_script_with_punctuation_included(self):
        """Test detection with punctuation when categories are included."""
        result = detect_script("Hello, World!", include_categories=True)
        self.assertIn("Latn", result)
        self.assertIn("punctuation", result)
        self.assertIn("spaces", result)

        self.assertEqual(result["Latn"], 76.92)  # 10 out of 13 chars
        self.assertEqual(
            result["punctuation"], 15.38
        )  # 2 out of 13 chars (comma and exclamation)
        self.assertEqual(result["spaces"], 7.69)  # 1 out of 13 chars

    def test_detect_script_exclude_categories(self):
        """Test detection without categories (default behavior)."""
        result = detect_script("Hello, World! 123")
        self.assertEqual(result, {"Latn": 100.0})
        self.assertNotIn("spaces", result)
        self.assertNotIn("punctuation", result)
        self.assertNotIn("numbers", result)

    def test_detect_script_min_threshold(self):
        """Test minimum threshold filtering."""
        # Text with moderate percentage of Arabic (12.2%)
        result = detect_script(
            "Hello World Hello World Hello World مرحبا", min_threshold=15.0
        )
        self.assertIn("Latn", result)
        self.assertNotIn("Arab", result)  # Should be below 15% threshold

        # With lower threshold, Arabic should appear
        result_low = detect_script(
            "Hello World Hello World Hello World مرحبا", min_threshold=10.0
        )
        self.assertIn("Arab", result_low)

    def test_detect_script_empty_and_invalid(self):
        """Test with empty strings and invalid inputs."""
        self.assertEqual(detect_script(""), {})
        self.assertEqual(detect_script(None), {})
        self.assertEqual(detect_script(123), {})

    def test_detect_script_special_characters(self):
        """Test with special characters and symbols."""
        result = detect_script("Price: $100.50")
        self.assertEqual(
            result, {"Latn": 100.0}
        )  # Only script chars counted by default

        # Test with categories included
        result_with_cats = detect_script("Price: $100.50", include_categories=True)
        self.assertIn("Latn", result_with_cats)
        self.assertIn("symbols", result_with_cats)
        self.assertIn("numbers", result_with_cats)
        self.assertIn("punctuation", result_with_cats)

    def test_detect_script_multiple_scripts(self):
        """Test with multiple different scripts."""
        # Latin, Arabic, Chinese, Cyrillic
        text = "Hello مرحبا 你好 Привет"
        result = detect_script(text)

        expected_scripts = {"Latn", "Arab", "Hans", "Cyrl"}
        actual_scripts = set(result.keys())
        self.assertEqual(actual_scripts, expected_scripts)

    def test_detect_script_syloti_nagri(self):
        """Test Syloti Nagri script detection (Sylo)."""
        # Use a couple of Syloti Nagri characters: U+A80A, U+A803
        text = "ꠊꠃ"
        result = detect_script(text)
        self.assertEqual(result, {"Sylo": 100.0})


class TestDetectScriptDetailed(unittest.TestCase):

    def test_detect_script_detailed_basic(self):
        """Test detailed analysis basic functionality."""
        result = detect_script_detailed("Hi!")

        self.assertEqual(result["total_chars"], 3)
        self.assertEqual(len(result["breakdown"]), 3)
        self.assertIn("Latn", result["summary"])
        self.assertIn("punctuation", result["summary"])

        # Check breakdown structure
        for char_info in result["breakdown"]:
            self.assertIn("char", char_info)
            self.assertIn("position", char_info)
            self.assertIn("code_point", char_info)
            self.assertTrue("script" in char_info or "category" in char_info)

    def test_detect_script_detailed_script_chars(self):
        """Test script_chars and category_chars collections."""
        result = detect_script_detailed("Hello, 123!")

        self.assertIn("Latn", result["script_chars"])
        self.assertIn("punctuation", result["category_chars"])
        self.assertIn("numbers", result["category_chars"])

        # Check that Latin characters are correctly collected
        latin_chars = result["script_chars"]["Latn"]
        expected_latin = ["H", "e", "l", "l", "o"]
        self.assertEqual(latin_chars, expected_latin)

    def test_detect_script_detailed_normalize_whitespace(self):
        """Test whitespace normalization."""
        text_with_tabs = "Hello\t\n\r World"
        result = detect_script_detailed(text_with_tabs, normalize_whitespace=True)

        # Should have replaced all whitespace with single spaces
        normalized_chars = [char_info["char"] for char_info in result["breakdown"]]
        normalized_text = "".join(normalized_chars)
        self.assertNotIn("\t", normalized_text)
        self.assertNotIn("\n", normalized_text)
        self.assertNotIn("\r", normalized_text)

    def test_detect_script_detailed_non_string(self):
        """Test with non-string input."""
        result = detect_script_detailed(None)

        expected = {
            "summary": {},
            "total_chars": 0,
            "breakdown": [],
            "script_chars": {},
            "category_chars": {},
        }
        self.assertEqual(result, expected)


class TestGetDominantScript(unittest.TestCase):

    def test_get_dominant_script_clear_majority(self):
        """Test with clear dominant script."""
        result = get_dominant_script("Hello World! This is a long English sentence.")
        self.assertEqual(result, "Latn")

    def test_get_dominant_script_arabic(self):
        """Test with Arabic dominant."""
        result = get_dominant_script("مرحبا بالعالم هذا نص طويل باللغة العربية")
        self.assertEqual(result, "Arab")

    def test_get_dominant_script_mixed_no_dominant(self):
        """Test with mixed scripts where none is dominant."""
        # More balanced text where no single script dominates
        result = get_dominant_script(
            "Hi مرحبا 你好 こんにちは हैलो", min_percentage=30.0
        )
        self.assertIsNone(result)  # No single script should reach 30% threshold

    def test_get_dominant_script_custom_threshold(self):
        """Test with custom threshold."""
        # With lower threshold, this should return a dominant script
        result = get_dominant_script("Hello مرحبا", min_percentage=20.0)
        self.assertIsNotNone(result)

        # With higher threshold, should return None
        result_high = get_dominant_script("Hello World مرحبا", min_percentage=80.0)
        self.assertIsNone(result_high)

    def test_get_dominant_script_empty(self):
        """Test with empty text."""
        result = get_dominant_script("")
        self.assertIsNone(result)


class TestIsScriptMixed(unittest.TestCase):

    def test_is_script_mixed_true(self):
        """Test with genuinely mixed scripts."""
        self.assertTrue(is_script_mixed("Hello مرحبا"))
        self.assertTrue(is_script_mixed("English 中文 العربية"))

    def test_is_script_mixed_false(self):
        """Test with single script."""
        self.assertFalse(is_script_mixed("Hello World"))
        self.assertFalse(is_script_mixed("مرحبا بالعالم"))
        self.assertFalse(is_script_mixed("你好世界"))

    def test_is_script_mixed_custom_threshold(self):
        """Test with custom threshold."""
        # Text with secondary script - but need higher threshold to exclude it
        text = "Hello مرحبا"  # 50% Latin, 50% Arabic

        # With threshold=60%, neither qualifies as significant enough
        self.assertFalse(is_script_mixed(text, threshold=60.0))

        # With lower threshold, should detect mixed
        self.assertTrue(is_script_mixed(text, threshold=20.0))

    def test_is_script_mixed_edge_cases(self):
        """Test edge cases."""
        self.assertFalse(is_script_mixed(""))
        self.assertFalse(is_script_mixed("123!@#"))  # Only categories, no scripts


class TestIntegration(unittest.TestCase):
    """Integration tests with more complex scenarios."""

    def test_multilingual_document(self):
        """Test with a realistic multilingual document."""
        text = """
        Welcome to our multilingual platform!
        مرحبا بكم في منصتنا متعددة اللغات!
        欢迎来到我们的多语言平台！
        Добро пожаловать на нашу многоязычную платформу!
        Price: $99.99
        Contact: support@example.com
        """

        result = detect_script(text)

        # Should contain multiple scripts (default excludes categories)
        self.assertIn("Latn", result)
        self.assertIn("Arab", result)
        self.assertIn("Hans", result)
        self.assertIn("Cyrl", result)

        # With categories included
        result_with_cats = detect_script(text, include_categories=True)
        self.assertIn("spaces", result_with_cats)
        self.assertIn("punctuation", result_with_cats)
        self.assertIn("numbers", result_with_cats)
        self.assertIn("symbols", result_with_cats)

        # Verify this is detected as mixed
        self.assertTrue(is_script_mixed(text))

        # Get detailed breakdown
        detailed = detect_script_detailed(text)
        self.assertGreater(detailed["total_chars"], 100)
        self.assertGreater(len(detailed["breakdown"]), 100)

    def test_consistency_between_functions(self):
        """Test that functions give consistent results when both use script-only mode."""
        text = "Hello مرحبا 你好"

        basic_result = detect_script(text)
        # Note: detailed function uses different logic (includes all chars in total)
        # This test focuses on the core functionality consistency

        # Check that the same scripts are detected
        self.assertIn("Latn", basic_result)
        self.assertIn("Arab", basic_result)
        self.assertIn("Hans", basic_result)

        # All percentages should add up to 100% in script-only mode
        total = sum(basic_result.values())
        self.assertAlmostEqual(total, 100.0, places=1)

    def test_performance_with_long_text(self):
        """Test with longer text to ensure reasonable performance."""
        # Create a long text with multiple scripts
        long_text = "Hello World! " * 100 + "مرحبا بالعالم! " * 100 + "你好世界！" * 100

        # This should complete without issues
        result = detect_script(long_text)
        self.assertIn("Latn", result)
        self.assertIn("Arab", result)
        self.assertIn("Hans", result)

        # Test detailed analysis too
        detailed = detect_script_detailed(long_text)
        self.assertEqual(detailed["total_chars"], len(long_text))

    def test_default_vs_categories_behavior(self):
        """Test the difference between default and categories-included behavior."""
        text = "Hello, World! 123"

        # Default behavior: only scripts
        default_result = detect_script(text)
        self.assertEqual(default_result, {"Latn": 100.0})

        # With categories: includes all character types
        categories_result = detect_script(text, include_categories=True)
        self.assertIn("Latn", categories_result)
        self.assertIn("punctuation", categories_result)
        self.assertIn("spaces", categories_result)
        self.assertIn("numbers", categories_result)

        # Verify the percentages are different
        self.assertNotEqual(default_result["Latn"], categories_result["Latn"])


if __name__ == "__main__":
    unittest.main()
