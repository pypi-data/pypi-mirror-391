import unittest
from unscript.unscript import clean_text


class TestCleanText(unittest.TestCase):
    def test_basic_input(self):
        """
        Test cases for basic valid and mixed language inputs.
        """
        self.assertEqual(
            clean_text("Hello, world!"), "hello, world!", "Failed on basic valid input"
        )
        self.assertEqual(
            clean_text("Hello 你好 こんにちは"),
            "hello 你好 こんにちは",
            "Failed on input with mixed languages",
        )
        self.assertEqual(
            clean_text("This is 1 example with 2 numbers."),
            "this is 1 example with 2 numbers.",
            "Failed on mixed text and numbers",
        )
        self.assertEqual(
            clean_text("Good morning!"), "good morning!", "Failed on simple greeting"
        )
        self.assertEqual(
            clean_text("Testing, testing, 1, 2, 3"),
            "testing, testing, 1, 2, 3",
            "Failed on comma separated items",
        )
        self.assertEqual(clean_text(""), "", "Failed on empty string")
        self.assertEqual(clean_text("A"), "a", "Failed on single character")

    def test_emojis(self):
        """
        Test cases for inputs containing emojis.
        """
        self.assertEqual(
            clean_text("Hello 😊! How are you?"),
            "hello ! how are you?",
            "Failed on input with emojis",
        )
        self.assertEqual(
            clean_text("Hello 😊😊! How are you?"),
            "hello ! how are you?",
            "Failed on input with multiple emojis",
        )
        self.assertEqual(clean_text("😊😊😊"), "", "Failed on input with only emojis")
        self.assertEqual(
            clean_text("مرحبا 😊 بكم في عالم البرمجة"),
            "مرحبا بكم في عالم البرمجة",
            "Failed on Arabic text with emojis",
        )
        self.assertEqual(
            clean_text("   Hello 😊😊   "),
            "hello",
            "Failed on input with excessive whitespace and emojis",
        )
        self.assertEqual(
            clean_text("👍👎❤️😊"), "", "Failed on input with various emoji types"
        )
        self.assertEqual(
            clean_text("Great job! 🎉🎊"), "great job!", "Failed on celebration emojis"
        )
        self.assertEqual(
            clean_text("🔥🔥 This is fire 🔥"), "this is fire", "Failed on fire emojis"
        )

    def test_repeated_characters(self):
        """
        Test cases for inputs with repeated characters.
        """
        self.assertEqual(
            clean_text("Heeeellooo!!!"),
            "heelloo!!",
            "Failed on input with repeated characters",
        )
        self.assertEqual(
            clean_text("Woooowww, that's coooolll!!!"),
            "wooww, that's cooll!!",
            "Failed on multiple sets of repeated characters",
        )
        self.assertEqual(
            clean_text("aaaaaaa"), "aa", "Failed on single letter repeated"
        )
        self.assertEqual(
            clean_text("Helllllloooooo"),
            "helloo",
            "Failed on different repeated patterns",
        )
        self.assertEqual(
            clean_text("Noooooo wayyyy!!!"),
            "noo wayy!!",
            "Failed on exclamation with repeated chars",
        )

    def test_arabic_text(self):
        """
        Test cases for inputs with Arabic text.
        """
        self.assertEqual(
            clean_text("مرحبا بكم في عالم البرمجة"),
            "مرحبا بكم في عالم البرمجة",
            "Failed on Arabic text",
        )
        self.assertEqual(
            clean_text("Hello in Arabic is مرحبا"),
            "hello in arabic is مرحبا",
            "Failed on mixed English and Arabic text",
        )
        self.assertEqual(
            clean_text("السلام عليكم ورحمة الله"),
            "السلام عليكم ورحمة الله",
            "Failed on longer Arabic phrase",
        )
        self.assertEqual(
            clean_text("Programming is البرمجة"),
            "programming is البرمجة",
            "Failed on English-Arabic mix",
        )

    def test_special_characters_and_punctuation(self):
        """
        Test cases for inputs with special characters and punctuation.
        Note: clean_text no longer removes punctuation - that's handled by clean_script/unscript
        """
        self.assertEqual(
            clean_text("This is a test @#$%^&*()"),
            "this is a test @#$%^&*()",
            "Failed on input with special characters",
        )
        self.assertEqual(
            clean_text("!Hello, world!?"),
            "!hello, world!?",
            "Failed on input with punctuation at start/end",
        )
        self.assertEqual(
            clean_text("This is a test @#$%^&*() @user"),
            "this is a test @#$%^&*()",
            "Failed on input with special characters and mentions",
        )
        self.assertEqual(
            clean_text("Test with .?!,;"),
            "test with .?!,;",
            "Failed on various punctuation marks",
        )
        self.assertEqual(
            clean_text("What's up?"),
            "what's up?",
            "Failed on apostrophe and question mark",
        )
        self.assertEqual(
            clean_text("It's a beautiful day!"),
            "it's a beautiful day!",
            "Failed on contractions",
        )
        self.assertEqual(
            clean_text("Don't worry, be happy!"),
            "don't worry, be happy!",
            "Failed on don't contraction",
        )
        self.assertEqual(
            clean_text("I'm going to the store."),
            "i'm going to the store.",
            "Failed on I'm contraction",
        )
        self.assertEqual(
            clean_text("We're all in this together."),
            "we're all in this together.",
            "Failed on we're contraction",
        )

    def test_numbers_only(self):
        """
        Test case for input with only numbers.
        """
        self.assertEqual(clean_text("123456"), "", "Failed on input with only numbers")
        self.assertEqual(
            clean_text("9876543210"), "", "Failed on different numbers only input"
        )
        self.assertEqual(clean_text("0"), "", "Failed on single zero")
        self.assertEqual(clean_text("42"), "", "Failed on two digit number")

    def test_whitespace(self):
        """
        Test cases for inputs with excessive whitespace.
        """
        self.assertEqual(
            clean_text("   Too   many   spaces   "),
            "too many spaces",
            "Failed on input with excessive whitespace",
        )
        self.assertEqual(
            clean_text("\n\tLeading and trailing whitespace\t\n"),
            "leading and trailing whitespace",
            "Failed on leading/trailing newlines and tabs",
        )
        self.assertEqual(
            clean_text("Multiple    spaces    between    words"),
            "multiple spaces between words",
            "Failed on multiple spaces between words",
        )
        self.assertEqual(clean_text("   "), "", "Failed on only whitespace")
        self.assertEqual(
            clean_text("\t\n\r"), "", "Failed on various whitespace characters"
        )

    def test_invalid_characters(self):
        """
        Test case for inputs with invalid characters.
        Note: clean_text now focuses on Unicode normalization rather than removing all invalid chars
        """
        # These tests focus on what clean_text should actually handle
        self.assertEqual(
            clean_text("This is a test with newlines\n\n"),
            "this is a test with newlines",
            "Failed on input with newlines",
        )
        self.assertEqual(
            clean_text("Another test with tabs\t\t"),
            "another test with tabs",
            "Failed on input with tabs",
        )

    def test_mentions_and_hashtags(self):
        """
        Test cases for inputs with mentions and hashtags.
        """
        self.assertEqual(
            clean_text("Hello @user! How are you?"),
            "hello ! how are you?",
            "Failed on input with mentions",
        )
        self.assertEqual(
            clean_text("Hello @user1 @user2! How are you?"),
            "hello ! how are you?",
            "Failed on input with multiple mentions",
        )
        self.assertEqual(
            clean_text("This is a #test!"),
            "this is a !",
            "Failed on input with hashtags",
        )
        self.assertEqual(
            clean_text("Hello @user 😊! How are you?"),
            "hello ! how are you?",
            "Failed on input with mixed emojis and mentions",
        )
        self.assertEqual(
            clean_text("#first #second @user3 final test."),
            "final test.",
            "Failed on mixed mentions and hashtags at different positions",
        )
        self.assertEqual(
            clean_text("@start of sentence"),
            "of sentence",
            "Failed on mention at start",
        )
        self.assertEqual(clean_text("#hashtag only"), "only", "Failed on hashtag only")
        self.assertEqual(
            clean_text("Check out #python and @developer"),
            "check out and",
            "Failed on hashtag and mention combination",
        )
        self.assertEqual(
            clean_text("Multiple #tags #here @user @another"),
            "multiple",
            "Failed on multiple tags and mentions",
        )

    def test_urls(self):
        """
        Test case for inputs with URLs.
        """
        self.assertEqual(
            clean_text("Check this link: https://example.com"),
            "check this link:",
            "Failed on input with URLs",
        )
        self.assertEqual(
            clean_text(
                "Visit our site at http://www.site.org and also https://another.com/path"
            ),
            "visit our site at and also",
            "Failed on multiple URLs",
        )
        self.assertEqual(
            clean_text("Text with a URL: example.com and more text"),
            "text with a url: and more text",
            "Failed on URL without scheme",
        )
        self.assertEqual(
            clean_text("Go to www.google.com for search"),
            "go to for search",
            "Failed on www URL",
        )
        self.assertEqual(
            clean_text("Email me at user@domain.com"),
            "email me at",
            "Failed on email address",
        )
        self.assertEqual(
            clean_text("ftp://files.example.com/file.zip"), "", "Failed on FTP URL only"
        )

    def test_edge_cases(self):
        """
        Test edge cases and complex combinations.
        Note: clean_text no longer removes all punctuation
        """
        self.assertEqual(
            clean_text("!!!???..."), "!!??..", "Failed on only punctuation"
        )
        self.assertEqual(
            clean_text("@@@###$$$"), "@@##$$", "Failed on only special characters"
        )
        self.assertEqual(
            clean_text("Hello!!!! @user #test https://example.com 😊😊😊"),
            "hello!!",
            "Failed on complex mixed input",
        )
        self.assertEqual(
            clean_text("   @user   #tag   https://site.com   😊   "),
            "",
            "Failed on spaced special elements",
        )
        self.assertEqual(
            clean_text("Normal text with @mention in #middle and url https://test.com"),
            "normal text with in and url",
            "Failed on mixed elements in sentence",
        )

    def test_case_sensitivity(self):
        """
        Test case sensitivity handling.
        """
        self.assertEqual(clean_text("HELLO WORLD"), "hello world", "Failed on all caps")
        self.assertEqual(
            clean_text("Hello World"), "hello world", "Failed on title case"
        )
        self.assertEqual(
            clean_text("hELLo WoRLd"), "hello world", "Failed on mixed case"
        )
        self.assertEqual(
            clean_text("MixED CaSe TeXt"),
            "mixed case text",
            "Failed on random case mix",
        )


if __name__ == "__main__":
    unittest.main()
