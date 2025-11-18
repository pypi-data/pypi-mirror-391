import unittest
from unscript.unscript import clean_text, clean_script


class TestCleanScript(unittest.TestCase):
    def test_latin_script(self):
        """Test Latin script cleaning with various configurations."""
        # Basic Latin text
        self.assertEqual(clean_script("Latn", "Hello World"), "Hello World")

        # Latin with numbers (default excludes numbers)
        self.assertEqual(clean_script("Latn", "Hello World 123"), "Hello World")

        # Latin with numbers (include numbers)
        self.assertEqual(
            clean_script("Latn", "Hello World 123", {"numbers": True}),
            "Hello World 123",
        )

        # Latin with punctuation (default excludes punctuation)
        self.assertEqual(clean_script("Latn", "Hello, World!"), "Hello World")

        # Latin with punctuation (include punctuation)
        self.assertEqual(
            clean_script("Latn", "Hello, World!", {"punctuation": "extended"}),
            "Hello, World!",
        )

        # Latin with symbols (default excludes symbols)
        self.assertEqual(clean_script("Latn", "Cost: $50"), "Cost")

        # Latin with symbols (include symbols)
        self.assertEqual(clean_script("Latn", "Cost: $50", {"symbols": True}), "Cost $")

        # Latin with mixed other scripts (should filter out non-Latin)
        self.assertEqual(clean_script("Latn", "Hello مرحبا 你好"), "Hello")

        # Latin extended characters
        self.assertEqual(clean_script("Latn", "Café résumé naïve"), "Café résumé naïve")

        # European languages with Latin script
        self.assertEqual(clean_script("Latn", "Hëllö Wörld"), "Hëllö Wörld")

        # Full configuration
        full_config = {"numbers": True, "punctuation": "extended", "symbols": True}
        self.assertEqual(
            clean_script("Latn", "Hello, World! $123.45", full_config),
            "Hello, World! $123.45",
        )

    def test_arabic_script(self):
        """Test Arabic script cleaning with various configurations."""
        # Basic Arabic text
        self.assertEqual(clean_script("Arab", "مرحبا بالعالم"), "مرحبا بالعالم")

        # Arabic with English (should filter out English)
        self.assertEqual(clean_script("Arab", "مرحبا Hello بالعالم"), "مرحبا بالعالم")

        # Arabic with Arabic numbers
        self.assertEqual(
            clean_script("Arab", "مرحبا ١٢٣ بالعالم", {"numbers": True}),
            "مرحبا ١٢٣ بالعالم",
        )

        # Arabic with Western numbers (should be filtered out)
        self.assertEqual(clean_script("Arab", "مرحبا 123 بالعالم"), "مرحبا بالعالم")

        # Arabic with punctuation
        self.assertEqual(
            clean_script("Arab", "مرحبا، بالعالم!", {"punctuation": "extended"}),
            "مرحبا، بالعالم!",
        )

        # Arabic presentation forms
        self.assertEqual(clean_script("Arab", "ﷺ ﷻ"), "ﷺ ﷻ")

        # Mixed Arabic scripts
        self.assertEqual(clean_script("Arab", "العربية ۱۲۳"), "العربية")

    def test_chinese_script(self):
        """Test Chinese (Hans) script cleaning."""
        # Simplified Chinese
        self.assertEqual(clean_script("Hans", "你好世界"), "你好世界")

        # Chinese with English (should filter out English)
        self.assertEqual(clean_script("Hans", "你好 Hello 世界"), "你好 世界")

        # Chinese with Japanese (should keep shared characters)
        self.assertEqual(clean_script("Hans", "你好 こんにちは 世界"), "你好 世界")

        # Chinese with punctuation
        self.assertEqual(
            clean_script("Hans", "你好，世界！", {"punctuation": "extended"}), "你好，世界！"
        )

    def test_punctuation_levels_ascii_mapping(self):
        """Boolean punctuation=True maps to ASCII level and excludes brackets."""
        # Latin
        self.assertEqual(
            clean_script("Latn", "Hello (World) [OK] {X} <Y>", {"punctuation": True}),
            "Hello World OK X Y",
        )
        # Arabic with ASCII quotes preserved and Arabic comma excluded at ASCII level
        s = 'قال: "هذا اختبار"، هل تُرى؟'
        # ASCII keeps ASCII quotes and ASCII punctuation but not Arabic comma/question
        self.assertEqual(
            clean_script("Arab", s, {"punctuation": True}),
            'قال: "هذا اختبار" هل تُرى',
        )

    def test_punctuation_levels_extended(self):
        """Extended level includes brackets and script-specific marks."""
        # Latin brackets retained under extended
        self.assertEqual(
            clean_script(
                "Latn",
                "Hello (World) [OK] {X} <Y>",
                {"punctuation": "extended"},
            ),
            "Hello (World) [OK] {X} <Y>",
        )
        # Arabic script-specific punctuation retained under extended
        self.assertEqual(
            clean_script(
                "Arab",
                'قال: "هذا اختبار"، هل تُرى؟',
                {"punctuation": "extended"},
            ),
            'قال: "هذا اختبار"، هل تُرى؟',
        )

    def test_punctuation_levels_all(self):
        """All level includes extended plus general punctuation like em dash."""
        # Em dash U+2014 kept under all
        self.assertEqual(
            clean_script(
                "Latn",
                "Alpha — Beta",
                {"punctuation": "all"},
            ),
            "Alpha — Beta",
        )

        # CJK symbols and punctuation
        self.assertEqual(
            clean_script("Hans", "你好。世界！", {"punctuation": "extended"}), "你好。世界！"
        )

    def test_japanese_script(self):
        """Test Japanese script cleaning."""
        # Japanese with Hiragana and Katakana
        self.assertEqual(
            clean_script("Jpan", "こんにちは カタカナ"), "こんにちは カタカナ"
        )

        # Japanese with Kanji
        self.assertEqual(clean_script("Jpan", "日本語"), "日本語")

        # Japanese with English (should filter out English)
        self.assertEqual(clean_script("Jpan", "こんにちは Hello"), "こんにちは")

        # Mixed Japanese scripts
        self.assertEqual(
            clean_script("Jpan", "ひらがな カタカナ 漢字"), "ひらがな カタカナ 漢字"
        )

    def test_cyrillic_script(self):
        """Test Cyrillic script cleaning."""
        # Russian text
        self.assertEqual(clean_script("Cyrl", "Привет мир"), "Привет мир")

        # Cyrillic with Latin (should filter out Latin)
        self.assertEqual(clean_script("Cyrl", "Привет Hello мир"), "Привет мир")

        # Extended Cyrillic
        self.assertEqual(clean_script("Cyrl", "Добро пожаловать"), "Добро пожаловать")

    def test_hebrew_script(self):
        """Test Hebrew script cleaning."""
        # Hebrew text
        self.assertEqual(clean_script("Hebr", "שלום עולם"), "שלום עולם")

        # Hebrew with English (should filter out English)
        self.assertEqual(clean_script("Hebr", "שלום Hello עולם"), "שלום עולם")

        # Hebrew with numbers
        self.assertEqual(clean_script("Hebr", "שלום 123 עולם"), "שלום עולם")

    def test_devanagari_script(self):
        """Test Devanagari script cleaning."""
        # Hindi text
        self.assertEqual(clean_script("Deva", "नमस्ते दुनिया"), "नमस्ते दुनिया")

        # Devanagari with English (should filter out English)
        self.assertEqual(clean_script("Deva", "नमस्ते Hello दुनिया"), "नमस्ते दुनिया")

        # Devanagari with numbers
        self.assertEqual(
            clean_script("Deva", "नमस्ते १२३ दुनिया", {"numbers": True}), "नमस्ते १२३ दुनिया"
        )

    def test_thai_script(self):
        """Test Thai script cleaning."""
        # Thai text
        self.assertEqual(clean_script("Thai", "สวัสดีโลก"), "สวัสดีโลก")

        # Thai with English (should filter out English)
        self.assertEqual(clean_script("Thai", "สวัสดี Hello โลก"), "สวัสดี โลก")

        # Thai with numbers
        self.assertEqual(
            clean_script("Thai", "สวัสดี ๑๒๓ โลก", {"numbers": True}), "สวัสดี ๑๒๓ โลก"
        )

    def test_korean_script(self):
        """Test Korean (Hangul) script cleaning."""
        # Korean text
        self.assertEqual(clean_script("Hang", "안녕하세요 세계"), "안녕하세요 세계")

        # Korean with English (should filter out English)
        self.assertEqual(
            clean_script("Hang", "안녕하세요 Hello 세계"), "안녕하세요 세계"
        )

        # Korean Jamo characters
        self.assertEqual(clean_script("Hang", "ㄱㄴㄷ ㅏㅑㅓ"), "ㄱㄴㄷ ㅏㅑㅓ")

    def test_greek_script(self):
        """Test Greek script cleaning."""
        # Greek text
        self.assertEqual(clean_script("Grek", "Γεια σας κόσμο"), "Γεια σας κόσμο")

        # Greek with Latin (should filter out Latin)
        self.assertEqual(clean_script("Grek", "Γεια Hello κόσμο"), "Γεια κόσμο")

    def test_georgian_script(self):
        """Test Georgian script cleaning."""
        # Georgian text
        self.assertEqual(clean_script("Geor", "გამარჯობა მსოფლიო"), "გამარჯობა მსოფლიო")

        # Georgian with Latin (should filter out Latin)
        self.assertEqual(
            clean_script("Geor", "გამარჯობა Hello მსოფლიო"), "გამარჯობა მსოფლიო"
        )

    def test_armenian_script(self):
        """Test Armenian script cleaning."""
        # Armenian text
        self.assertEqual(clean_script("Armn", "Բարև աշխարհ"), "Բարև աշխարհ")

        # Armenian with Latin (should filter out Latin)
        self.assertEqual(clean_script("Armn", "Բարև Hello աշխարհ"), "Բարև աշխարհ")

    def test_ethiopic_script(self):
        """Test Ethiopic script cleaning."""
        # Ethiopic text (Amharic)
        self.assertEqual(clean_script("Ethi", "ሰላም ዓለም"), "ሰላም ዓለም")

        # Ethiopic with Latin (should filter out Latin)
        self.assertEqual(clean_script("Ethi", "ሰላም Hello ዓለም"), "ሰላም ዓለም")

    def test_mongolian_script(self):
        """Test Mongolian script cleaning."""
        # Mongolian text
        self.assertEqual(clean_script("Mong", "ᠰᠠᠢᠨ ᠪᠠᠢᠨᠠ ᠤᠤ"), "ᠰᠠᠢᠨ ᠪᠠᠢᠨᠠ ᠤᠤ")

        # Mongolian with Latin (should filter out Latin)
        self.assertEqual(clean_script("Mong", "ᠰᠠᠢᠨ Hello ᠤᠤ"), "ᠰᠠᠢᠨ ᠤᠤ")

    def test_spaces_configuration(self):
        """Test space handling across different scripts."""
        # Default includes spaces
        self.assertEqual(clean_script("Latn", "Hello World"), "Hello World")

        # Explicitly exclude spaces
        self.assertEqual(
            clean_script("Latn", "Hello World", {"spaces": False}), "HelloWorld"
        )

        # Multiple spaces should be collapsed
        self.assertEqual(clean_script("Latn", "Hello    World"), "Hello World")

    def test_numbers_configuration(self):
        """Test number handling across different scripts."""
        # Western digits
        self.assertEqual(
            clean_script("Latn", "Hello 123", {"numbers": True}), "Hello 123"
        )

        # Arabic-Indic digits
        self.assertEqual(
            clean_script("Arab", "مرحبا ١٢٣", {"numbers": True}), "مرحبا ١٢٣"
        )

        # Devanagari digits
        self.assertEqual(
            clean_script("Deva", "नमस्ते १२३", {"numbers": True}), "नमस्ते १२३"
        )

        # Thai digits
        self.assertEqual(
            clean_script("Thai", "สวัสดี ๑๒๓", {"numbers": True}), "สวัสดี ๑๒๓"
        )

    def test_punctuation_configuration(self):
        """Test punctuation handling across different scripts."""
        # Basic punctuation
        self.assertEqual(
            clean_script("Latn", "Hello, World!", {"punctuation": True}),
            "Hello, World!",
        )

        # Arabic punctuation
        self.assertEqual(
            clean_script("Arab", "مرحبا، العالم؟", {"punctuation": "extended"}),
            "مرحبا، العالم؟",
        )

        # CJK punctuation
        self.assertEqual(
            clean_script("Hans", "你好，世界！", {"punctuation": "extended"}), "你好，世界！"
        )

    def test_symbols_configuration(self):
        """Test symbol handling across different scripts."""
        # Currency symbols
        self.assertEqual(
            clean_script("Latn", "Cost $50 €25", {"symbols": True}), "Cost $ €"
        )

        # Mathematical symbols
        self.assertEqual(
            clean_script("Latn", "2 + 2 = 4", {"symbols": True, "numbers": True}),
            "2 + 2 = 4",
        )

        # Various symbols
        self.assertEqual(
            clean_script("Latn", "Email: user@domain.com", {"symbols": True}),
            "Email user@domain com",
        )

    def test_arabic_quotes_with_symbols_flag(self):
        """Arabic quotes should be preserved with punctuation=True regardless of symbols flag."""
        s = 'قال: "هذا اختبار"، هل تُرى؟'
        # symbols=True keeps everything including quotes (extended to include Arabic punctuation)
        self.assertEqual(
            clean_script("Arab", s, {"numbers": True, "punctuation": "extended", "spaces": True, "symbols": True}),
            s,
        )
        # symbols=False should still keep quotes as punctuation
        self.assertEqual(
            clean_script("Arab", s, {"numbers": True, "punctuation": "extended", "spaces": True, "symbols": False}),
            s,
        )

    def test_edge_cases(self):
        """Test edge cases for clean_script."""
        # Empty string
        self.assertEqual(clean_script("Latn", ""), "")

        # Non-string input
        self.assertEqual(clean_script("Latn", None), None)

        # Unknown script (should return original text)
        self.assertEqual(clean_script("Unknown", "Hello World"), "Hello World")

        # Text with only filtered characters
        self.assertEqual(clean_script("Latn", "123!@#"), "")

        # Mixed scripts with different configurations
        mixed_text = "Hello مرحبا 你好 123 !@#"
        self.assertEqual(clean_script("Latn", mixed_text), "Hello")
        self.assertEqual(clean_script("Arab", mixed_text), "مرحبا")
        self.assertEqual(clean_script("Hans", mixed_text), "你好")

    def test_comprehensive_mixed_scripts(self):
        """Test comprehensive mixed script scenarios."""
        complex_text = "Hello مرحبا שלום Привет 你好 こんにちは Γεια σας 123 !@# $%^"

        # Test each script extracts only its characters
        self.assertEqual(clean_script("Latn", complex_text), "Hello")
        self.assertEqual(clean_script("Arab", complex_text), "مرحبا")
        self.assertEqual(clean_script("Hebr", complex_text), "שלום")
        self.assertEqual(clean_script("Cyrl", complex_text), "Привет")
        self.assertEqual(clean_script("Hans", complex_text), "你好")
        self.assertEqual(clean_script("Jpan", complex_text), "你好 こんにちは")
        self.assertEqual(clean_script("Grek", complex_text), "Γεια σας")

    def test_whitespace_normalization(self):
        """Test whitespace normalization across scripts."""
        # Multiple spaces
        self.assertEqual(clean_script("Latn", "Hello    World"), "Hello World")

        # Leading/trailing spaces
        self.assertEqual(clean_script("Latn", "  Hello World  "), "Hello World")

        # Mixed whitespace characters
        self.assertEqual(clean_script("Latn", "Hello\t\nWorld"), "Hello World")

    def test_additional_scripts(self):
        """Test additional script ranges."""
        # Bengali script
        self.assertEqual(clean_script("Beng", "বাংলা ভাষা"), "বাংলা ভাষা")
        self.assertEqual(clean_script("Beng", "বাংলা Hello ভাষা"), "বাংলা ভাষা")

        # Gujarati script
        self.assertEqual(clean_script("Gujr", "ગુજરાતી ભાષા"), "ગુજરાતી ભાષા")
        self.assertEqual(clean_script("Gujr", "ગુજરાતી Hello ભાષા"), "ગુજરાતી ભાષા")

        # Gurmukhi (Punjabi) script
        self.assertEqual(clean_script("Guru", "ਪੰਜਾਬੀ ਭਾਸ਼ਾ"), "ਪੰਜਾਬੀ ਭਾਸ਼ਾ")
        self.assertEqual(clean_script("Guru", "ਪੰਜਾਬੀ Hello ਭਾਸ਼ਾ"), "ਪੰਜਾਬੀ ਭਾਸ਼ਾ")

        # Tamil script
        self.assertEqual(clean_script("Taml", "தமிழ் மொழி"), "தமிழ் மொழி")
        self.assertEqual(clean_script("Taml", "தமிழ் Hello மொழி"), "தமிழ் மொழி")

        # Telugu script
        self.assertEqual(clean_script("Telu", "తెలుగు భాష"), "తెలుగు భాష")
        self.assertEqual(clean_script("Telu", "తెలుగు Hello భాష"), "తెలుగు భాష")

        # Kannada script
        self.assertEqual(clean_script("Knda", "ಕನ್ನಡ ಭಾಷೆ"), "ಕನ್ನಡ ಭಾಷೆ")
        self.assertEqual(clean_script("Knda", "ಕನ್ನಡ Hello ಭಾಷೆ"), "ಕನ್ನಡ ಭಾಷೆ")

        # Malayalam script
        self.assertEqual(clean_script("Mlym", "മലയാളം ഭാഷ"), "മലയാളം ഭാഷ")
        self.assertEqual(clean_script("Mlym", "മലയാളം Hello ഭാഷ"), "മലയാളം ഭാഷ")

        # Oriya script
        self.assertEqual(clean_script("Orya", "ଓଡ଼ିଆ ଭାଷା"), "ଓଡ଼ିଆ ଭାଷା")
        self.assertEqual(clean_script("Orya", "ଓଡ଼ିଆ Hello ଭାଷା"), "ଓଡ଼ିଆ ଭାଷା")

        # Sinhala script
        self.assertEqual(clean_script("Sinh", "සිංහල භාෂාව"), "සිංහල භාෂාව")
        self.assertEqual(clean_script("Sinh", "සිංහල Hello භාෂාව"), "සිංහල භාෂාව")

        # Myanmar script
        self.assertEqual(clean_script("Mymr", "မြန်မာ ဘာသာ"), "မြန်မာ ဘာသာ")
        self.assertEqual(clean_script("Mymr", "မြန်မာ Hello ဘာသာ"), "မြန်မာ ဘာသာ")

        # Lao script
        self.assertEqual(clean_script("Laoo", "ພາສາລາວ"), "ພາສາລາວ")
        self.assertEqual(clean_script("Laoo", "ພາສາ Hello ລາວ"), "ພາສາ ລາວ")

        # Tibetan script
        self.assertEqual(clean_script("Tibt", "བོད་ཡིག"), "བོད་ཡིག")
        self.assertEqual(clean_script("Tibt", "བོད་ Hello ཡིག"), "བོད་ ཡིག")

        # Khmer script
        self.assertEqual(clean_script("Khmr", "ភាសាខ្មែរ"), "ភាសាខ្មែរ")
        self.assertEqual(clean_script("Khmr", "ភាសា Hello ខ្មែរ"), "ភាសា ខ្មែរ")

    def test_traditional_chinese(self):
        """Test Traditional Chinese (Hant) script cleaning."""
        # Traditional Chinese
        self.assertEqual(clean_script("Hant", "你好世界"), "你好世界")

        # Traditional Chinese with English (should filter out English)
        self.assertEqual(clean_script("Hant", "你好 Hello 世界"), "你好 世界")

        # Traditional Chinese with punctuation
        self.assertEqual(
            clean_script("Hant", "你好，世界！", {"punctuation": "extended"}), "你好，世界！"
        )

    def test_number_systems_comprehensive(self):
        """Test various number systems with their respective scripts."""
        # Bengali digits
        self.assertEqual(
            clean_script("Beng", "বাংলা ০১২৩৪৫৬৭৮৯", {"numbers": True}),
            "বাংলা ০১২৩৪৫৬৭৮৯",
        )

        # Gujarati digits
        self.assertEqual(
            clean_script("Gujr", "ગુજરાતી ૦૧૨૩૪૫૬૭૮૯", {"numbers": True}),
            "ગુજરાતી ૦૧૨૩૪૫૬૭૮૯",
        )

        # Gurmukhi digits
        self.assertEqual(
            clean_script("Guru", "ਪੰਜਾਬੀ ੦੧੨੩੪੫੬੭੮੯", {"numbers": True}),
            "ਪੰਜਾਬੀ ੦੧੨੩੪੫੬੭੮੯",
        )

        # Telugu digits
        self.assertEqual(
            clean_script("Telu", "తెలుగు ౦౧౨౩౪౫౬౭౮౯", {"numbers": True}),
            "తెలుగు ౦౧౨౩౪౫౬౭౮౯",
        )

        # Kannada digits
        self.assertEqual(
            clean_script("Knda", "ಕನ್ನಡ ೦೧೨೩೪೫೬೭೮೯", {"numbers": True}),
            "ಕನ್ನಡ ೦೧೨೩೪೫೬೭೮೯",
        )

        # Malayalam digits
        self.assertEqual(
            clean_script("Mlym", "മലയാളം ൦൧൨൩൪൫൬൭൮൯", {"numbers": True}),
            "മലയാളം ൦൧൨൩൪൫൬൭൮൯",
        )

        # Oriya digits
        self.assertEqual(
            clean_script("Orya", "ଓଡ଼ିଆ ୦୧୨୩୪୫୬୭୮୯", {"numbers": True}), "ଓଡ଼ିଆ ୦୧୨୩୪୫୬୭୮୯"
        )

        # Sinhala digits
        self.assertEqual(
            clean_script("Sinh", "සිංහල ෦෧෨෩෪෫෬෭෮෯", {"numbers": True}),
            "සිංහල ෦෧෨෩෪෫෬෭෮෯",
        )

        # Myanmar digits
        self.assertEqual(
            clean_script("Mymr", "မြန်မာ ၀၁၂၃၄၅၆၇၈၉", {"numbers": True}),
            "မြန်မာ ၀၁၂၃၄၅၆၇၈၉",
        )

        # Lao digits
        self.assertEqual(
            clean_script("Laoo", "ລາວ ໐໑໒໓໔໕໖໗໘໙", {"numbers": True}), "ລາວ ໐໑໒໓໔໕໖໗໘໙"
        )

        # Tibetan digits
        self.assertEqual(
            clean_script("Tibt", "བོད ༠༡༢༣༤༥༦༧༨༩", {"numbers": True}), "བོད ༠༡༢༣༤༥༦༧༨༩"
        )

        # Khmer digits
        self.assertEqual(
            clean_script("Khmr", "ខ្មែរ ០១២៣៤៥៦៧៨៩", {"numbers": True}),
            "ខ្មែរ ០១២៣៤៥៦៧៨៩",
        )

        # Mongolian digits
        self.assertEqual(
            clean_script("Mong", "ᠮᠣᠩᠭᠣᠯ ᠑᠘᠑᠘", {"numbers": True}), "ᠮᠣᠩᠭᠣᠯ ᠑᠘᠑᠘"
        )

    def test_script_specific_punctuation(self):
        """Test script-specific punctuation marks."""
        # Arabic punctuation
        self.assertEqual(
            clean_script("Arab", "العربية، هذا؟ نعم!", {"punctuation": "extended"}),
            "العربية، هذا؟ نعم!",
        )

        # Devanagari punctuation (using danda)
        self.assertEqual(
            clean_script("Deva", "हिन्दी। यह है॥", {"punctuation": "extended"}), "हिन्दी। यह है॥"
        )

        # CJK punctuation
        self.assertEqual(
            clean_script("Hans", "中文。这是！", {"punctuation": "extended"}), "中文。这是！"
        )
        self.assertEqual(
            clean_script("Jpan", "日本語。これは！", {"punctuation": "extended"}),
            "日本語。これは！",
        )

    def test_currency_symbols_with_scripts(self):
        """Test currency symbols with different scripts."""
        # Arabic with various currency symbols
        self.assertEqual(
            clean_script("Arab", "العملة $ € ¥ £", {"symbols": True}), "العملة $ € ¥ £"
        )

        # Devanagari with rupee symbol
        self.assertEqual(
            clean_script("Deva", "भारतीय ₹", {"symbols": True}), "भारतीय ₹"
        )

        # Thai with baht symbol
        self.assertEqual(clean_script("Thai", "ไทย ฿", {"symbols": True}), "ไทย ฿")

    def test_emoji_filtering_across_scripts(self):
        """Test that emojis are filtered out across all scripts."""
        # Emojis should be filtered out regardless of script
        self.assertEqual(clean_script("Latn", "Hello 😊 World"), "Hello World")
        self.assertEqual(clean_script("Arab", "مرحبا 😊 العالم"), "مرحبا العالم")
        self.assertEqual(clean_script("Hans", "你好 😊 世界"), "你好 世界")
        self.assertEqual(clean_script("Jpan", "こんにちは 😊 世界"), "こんにちは 世界")
        self.assertEqual(clean_script("Deva", "नमस्ते 😊 दुनिया"), "नमस्ते दुनिया")
        self.assertEqual(clean_script("Thai", "สวัสดี 😊 โลก"), "สวัสดี โลก")

    def test_mixed_configurations(self):
        """Test complex mixed configurations."""
        full_config = {"numbers": True, "punctuation": "extended", "symbols": True}

        # Latin with everything
        self.assertEqual(
            clean_script("Latn", "Hello, World! Cost: $123.45 (20% off)", full_config),
            "Hello, World! Cost: $123.45 (20% off)",
        )

        # Arabic with everything
        self.assertEqual(
            clean_script("Arab", "مرحبا، العالم! السعر: ١٢٣ ريال", full_config),
            "مرحبا، العالم! السعر: ١٢٣ ريال",
        )

        # Chinese with everything
        self.assertEqual(
            clean_script("Hans", "你好，世界！价格：￥123", full_config),
            "你好，世界！价格：￥123",
        )

    def test_script_boundary_cases(self):
        """Test edge cases around script boundaries."""
        # Text that becomes empty after filtering
        self.assertEqual(clean_script("Latn", "123 !@# $%^"), "")
        self.assertEqual(clean_script("Arab", "123 !@# $%^"), "")

        # Text with only spaces
        self.assertEqual(clean_script("Latn", "   "), "")
        self.assertEqual(clean_script("Arab", "   "), "")

        # Mixed scripts with spaces only preserved
        self.assertEqual(clean_script("Latn", "Hello مرحبا"), "Hello")
        self.assertEqual(clean_script("Arab", "Hello مرحبا"), "مرحبا")

    def test_comprehensive_script_punctuation(self):
        """Test script-specific punctuation marks across various scripts."""

        # Test cases for script-specific punctuation
        test_cases = [
            # (script, text, expected_without_punct, expected_with_punct)
            ("Deva", "नमस्ते। यह है॥", "नमस्ते यह है", "नमस्ते। यह है॥"),
            ("Mymr", "မင်္ဂလာပါ။", "မင်္ဂလာပါ", "မင်္ဂလာပါ။"),
            ("Khmr", "សួស្តី។", "សួស្តី", "សួស្តី។"),
            ("Tibt", "བཀྲ་ཤིས།", "བཀྲ་ཤིས", "བཀྲ་ཤིས།"),
            ("Hans", "你好。世界！", "你好 世界", "你好。世界！"),
            ("Arab", "السلام، عليكم؟", "السلام عليكم", "السلام، عليكم؟"),
        ]

        for script, text, expected_no_punct, expected_with_punct in test_cases:
            with self.subTest(script=script, text=text):
                # Test without punctuation (default)
                result_no_punct = clean_script(script, text)
                self.assertEqual(
                    result_no_punct,
                    expected_no_punct,
                    f"Failed for {script} without punctuation",
                )

                # Test with punctuation enabled
                result_with_punct = clean_script(script, text, {"punctuation": "extended"})
                self.assertEqual(
                    result_with_punct,
                    expected_with_punct,
                    f"Failed for {script} with punctuation",
                )


if __name__ == "__main__":
    unittest.main()
