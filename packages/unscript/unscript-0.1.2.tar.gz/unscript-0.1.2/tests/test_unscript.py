import unittest
from unscript.unscript import unscript


class TestUnscript(unittest.TestCase):
    def test_basic_latin_unscript(self):
        """Test basic Latin script cleaning with unscript function."""
        # Basic Latin text with mentions and URLs
        result = unscript("Latn", "Hello @user! Check https://example.com 😊")
        self.assertEqual(result, "hello check")

        # Latin text with punctuation (should be removed by default)
        result = unscript("Latn", "Hello, world! How are you?")
        self.assertEqual(result, "hello world how are you")

        # Latin text with mixed scripts (should filter out non-Latin)
        result = unscript("Latn", "Hello مرحبا 你好 world!")
        self.assertEqual(result, "hello world")

    def test_basic_arabic_unscript(self):
        """Test basic Arabic script cleaning with unscript function."""
        # Basic Arabic text
        result = unscript("Arab", "مرحبا بالعالم @user!")
        self.assertEqual(result, "مرحبا بالعالم")

        # Arabic with mixed scripts (should filter out non-Arabic)
        result = unscript("Arab", "مرحبا Hello بالعالم!")
        self.assertEqual(result, "مرحبا بالعالم")

        # Arabic with URLs and emojis
        result = unscript("Arab", "مرحبا https://example.com 😊 بالعالم")
        self.assertEqual(result, "مرحبا بالعالم")

    def test_unscript_with_config(self):
        """Test unscript function with different configurations."""
        # Include punctuation
        result = unscript("Latn", "Hello, world! @user", {"punctuation": True})
        self.assertEqual(result, "hello, world!")

        # Include numbers
        result = unscript("Latn", "Hello 123 world @user", {"numbers": True})
        self.assertEqual(result, "hello 123 world")

        # Include symbols
        result = unscript("Latn", "Cost $50 @user", {"symbols": True})
        self.assertEqual(result, "cost $")

        # Full config
        full_config = {"numbers": True, "punctuation": True, "symbols": True}
        result = unscript("Latn", "Hello, world! $123.45 @user", full_config)
        self.assertEqual(result, "hello, world! $123.45")

    def test_unscript_with_arabic_config(self):
        """Test unscript function with Arabic script and configurations."""
        # Arabic with punctuation
        result = unscript("Arab", "مرحبا، بالعالم! @user", {"punctuation": "extended"})
        self.assertEqual(result, "مرحبا، بالعالم!")

        # Arabic with Arabic numbers
        result = unscript("Arab", "مرحبا ١٢٣ بالعالم @user", {"numbers": True})
        self.assertEqual(result, "مرحبا ١٢٣ بالعالم")

    def test_unscript_repeated_characters(self):
        """Test that unscript handles repeated character collapsing."""
        # Latin script
        result = unscript("Latn", "Heeeellooo @user!!!")
        self.assertEqual(result, "heelloo")

        # With punctuation enabled
        result = unscript("Latn", "Heeeellooo @user!!!", {"punctuation": True})
        self.assertEqual(result, "heelloo !!")

    def test_unscript_case_handling(self):
        """Test case sensitivity options in unscript."""
        # Default lowercase
        result = unscript("Latn", "HELLO WORLD @user!")
        self.assertEqual(result, "hello world")

        # Preserve case
        result = unscript("Latn", "HELLO WORLD @user!", lowercase=False)
        self.assertEqual(result, "HELLO WORLD")

        # Preserve case with config
        result = unscript(
            "Latn", "HELLO, WORLD! @user", {"punctuation": True}, lowercase=False
        )
        self.assertEqual(result, "HELLO, WORLD!")

    def test_unscript_empty_and_edge_cases(self):
        """Test unscript with empty strings and edge cases."""
        # Empty string
        result = unscript("Latn", "")
        self.assertEqual(result, "")

        # Only mentions and URLs
        result = unscript("Latn", "@user #hashtag https://example.com")
        self.assertEqual(result, "")

        # Only emojis
        result = unscript("Latn", "😊😊😊")
        self.assertEqual(result, "")

        # Only numbers (should return empty due to clean_text's number-only check)
        result = unscript("Latn", "123456", {"numbers": True})
        self.assertEqual(result, "")

    def test_unscript_mixed_content(self):
        """Test unscript with complex mixed content."""
        complex_text = (
            "Hello @user! مرحبا 你好 Check https://example.com 😊 #hashtag $100.99"
        )

        # Latin script only
        result = unscript("Latn", complex_text)
        self.assertEqual(result, "hello check")

        # Latin with numbers and symbols
        result = unscript("Latn", complex_text, {"numbers": True, "symbols": True})
        self.assertEqual(result, "hello check $100.99")

        # Arabic script only
        result = unscript("Arab", complex_text)
        self.assertEqual(result, "مرحبا")

    def test_unscript_whitespace_handling(self):
        """Test that unscript properly handles whitespace."""
        # Multiple spaces
        result = unscript("Latn", "Hello    @user   world   !")
        self.assertEqual(result, "hello world")

        # Newlines and tabs
        result = unscript("Latn", "Hello\n@user\tworld!")
        self.assertEqual(result, "hello world")

    def test_unscript_chinese_script(self):
        """Test unscript with Chinese script."""
        # Simplified Chinese
        result = unscript("Hans", "你好 @user world! 😊")
        self.assertEqual(result, "你好")

        # Chinese with punctuation
        result = unscript("Hans", "你好，世界! @user", {"punctuation": "extended"})
        self.assertEqual(result, "你好，世界!")

    def test_unscript_invalid_script(self):
        """Test unscript behavior with invalid script codes."""
        # Unknown script should return text processed only by clean_text
        result = unscript("Unknown", "Hello @user world!")
        self.assertEqual(result, "hello world!")

    def test_unscript_non_string_input(self):
        """Test unscript with non-string inputs."""
        result = unscript("Latn", None)
        self.assertEqual(result, "")

        result = unscript("Latn", 123)
        self.assertEqual(result, "")

    def test_unscript_urls_and_domains(self):
        """Test unscript's handling of various URL formats."""
        # HTTP/HTTPS URLs
        result = unscript("Latn", "Visit https://example.com and http://test.org")
        self.assertEqual(result, "visit and")

        # FTP URLs
        result = unscript("Latn", "Download ftp://files.example.com/file.zip")
        self.assertEqual(result, "download")

        # WWW URLs
        result = unscript("Latn", "Go to www.google.com for search")
        self.assertEqual(result, "go to for search")

        # Email addresses
        result = unscript("Latn", "Contact user@domain.com for help")
        self.assertEqual(result, "contact for help")

        # Domain names
        result = unscript("Latn", "Visit example.com and test.org")
        self.assertEqual(result, "visit and")

    def test_unscript_hashtags_and_mentions(self):
        """Test unscript's handling of hashtags and mentions."""
        # Various mention formats
        result = unscript("Latn", "Hello @user and @@admin also +support")
        self.assertEqual(result, "hello and also")

        # Hashtags
        result = unscript("Latn", "Love #python and #coding!")
        self.assertEqual(result, "love and")

        # Mixed mentions and hashtags
        result = unscript("Latn", "#trending @user content +follow")
        self.assertEqual(result, "content")


if __name__ == "__main__":
    unittest.main()
