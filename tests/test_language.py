import unittest

from src.services.language import (
    detect_language,
    get_language_label,
    get_string,
    normalize_language_code,
    resolve_query_language,
    resolve_ui_language,
)


class LanguageServiceTests(unittest.TestCase):
    def test_detects_russian_from_cyrillic_text(self):
        self.assertEqual(detect_language("Когда дедлайн на стипендию?"), "ru")

    def test_detects_kazakh_from_specific_letters(self):
        self.assertEqual(detect_language("Жатақханаға құжаттар қашан керек?"), "kk")

    def test_detects_kazakh_without_kazakh_specific_letters(self):
        self.assertEqual(detect_language("Келеси дедлайн кашан"), "kk")

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

    def test_resolve_ui_language_prefers_saved_preference(self):
        self.assertEqual(resolve_ui_language("kk", "When is the deadline?", "en-US"), "kk")

    def test_resolve_ui_language_falls_back_to_query_detection(self):
        self.assertEqual(resolve_ui_language(None, "When is the deadline?", "ru-RU"), "en")

    def test_resolve_query_language_uses_current_message(self):
        self.assertEqual(resolve_query_language("When is the housing deadline?", "ru-RU"), "en")

    def test_get_string_returns_localized_messages(self):
        self.assertIn("По этому вопросу ничего не нашлось", get_string("ru", "no_results"))
        self.assertIn("Бұл сұрақ бойынша ештеңе табылмады", get_string("kk", "no_results"))
        self.assertIn("No relevant messages found", get_string("en", "no_results"))

    def test_get_language_label_returns_human_readable_name(self):
        self.assertEqual(get_language_label("kk"), "Қазақша")


if __name__ == "__main__":
    unittest.main()
