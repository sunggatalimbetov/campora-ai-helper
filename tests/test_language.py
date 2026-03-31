import unittest

from src.services.language import (
    get_language_label,
    get_string,
    normalize_language_code,
    resolve_ui_language,
)


class LanguageServiceTests(unittest.TestCase):
    def test_normalizes_supported_telegram_language_codes(self):
        self.assertEqual(normalize_language_code("ru-RU"), "ru")
        self.assertEqual(normalize_language_code("kk_KZ"), "kk")
        self.assertEqual(normalize_language_code("en"), "en")

    def test_resolve_ui_language_prefers_saved_preference(self):
        self.assertEqual(resolve_ui_language("kk", "When is the deadline?", "en-US"), "kk")

    def test_resolve_ui_language_detects_russian_from_query(self):
        self.assertEqual(resolve_ui_language(None, "Когда дедлайн?", "en-US"), "ru")

    def test_resolve_ui_language_detects_kazakh_from_query(self):
        self.assertEqual(resolve_ui_language(None, "КС-ке проходной балл қанша?", "en-US"), "kk")

    def test_resolve_ui_language_detects_english_from_query(self):
        self.assertEqual(resolve_ui_language(None, "What SAT score do I need?", "ru-RU"), "en")

    def test_resolve_ui_language_falls_back_to_telegram_code(self):
        self.assertEqual(resolve_ui_language(None, None, "ru-RU"), "ru")

    def test_resolve_ui_language_defaults_to_english_without_anything(self):
        self.assertEqual(resolve_ui_language(None, None, None), "en")

    def test_get_string_returns_localized_messages(self):
        self.assertIn("По этому вопросу ничего не нашлось", get_string("ru", "no_results"))
        self.assertIn("Бұл сұрақ бойынша ештеңе табылмады", get_string("kk", "no_results"))
        self.assertIn("No relevant messages found", get_string("en", "no_results"))
        self.assertIn("удалены из базы", get_string("ru", "optout_success"))
        self.assertIn("қайтадан индекстеледі", get_string("kk", "optin_success"))
        self.assertIn("no longer be indexed", get_string("en", "optout_success"))
        self.assertIn("English", get_string("en", "language_command", language_label="English"))
        self.assertIn("Русский", get_string("ru", "language_updated", language_label="Русский"))

    def test_get_language_label_returns_human_readable_name(self):
        self.assertEqual(get_language_label("kk"), "Қазақша")


if __name__ == "__main__":
    unittest.main()
