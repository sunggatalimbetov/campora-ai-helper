import unittest

from src.services.language import detect_language, get_no_results_message, normalize_language_code


class LanguageServiceTests(unittest.TestCase):
    def test_detects_russian_from_cyrillic_text(self):
        self.assertEqual(detect_language("Когда дедлайн на стипендию?"), "ru")

    def test_detects_kazakh_from_specific_letters(self):
        self.assertEqual(detect_language("Жатақханаға құжаттар қашан керек?"), "kk")

    def test_detects_english_from_latin_text(self):
        self.assertEqual(detect_language("When is the housing deadline?"), "en")

    def test_falls_back_to_telegram_language_code(self):
        self.assertEqual(detect_language("12345", telegram_language_code="kk-KZ"), "kk")

    def test_defaults_to_russian_when_language_is_ambiguous(self):
        self.assertEqual(detect_language("12345"), "ru")

    def test_normalizes_supported_telegram_language_codes(self):
        self.assertEqual(normalize_language_code("ru-RU"), "ru")
        self.assertEqual(normalize_language_code("kk_KZ"), "kk")
        self.assertEqual(normalize_language_code("en"), "en")

    def test_returns_localized_no_results_message(self):
        self.assertIn("По этому вопросу ничего не нашлось", get_no_results_message("Когда дедлайн?"))
        self.assertIn("Бұл сұрақ бойынша ештеңе табылмады", get_no_results_message("Жатақхана бар ма?"))
        self.assertIn("No relevant messages found", get_no_results_message("What about housing?"))


if __name__ == "__main__":
    unittest.main()
