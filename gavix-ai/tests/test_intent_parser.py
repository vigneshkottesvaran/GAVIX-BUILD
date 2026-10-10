
import unittest

from src.core.intent_parser import normalize_command, parse_intent


class TestIntentParser(unittest.TestCase):

    def test_launch_chrome(self):
        self.assertEqual(
            parse_intent("Launch Chrome"),
            {"intent": "open_chrome"},
        )

    def test_open_downloads(self):
        self.assertEqual(
            parse_intent("Open Downloads"),
            {"intent": "open_folder", "target": "downloads"},
        )

    def test_find_pdf_files(self):
        self.assertEqual(
            parse_intent("Find PDF files"),
            {"intent": "find_files", "target": "pdf files"},
        )

    def test_delete_file(self):
        self.assertEqual(
            parse_intent("Delete file"),
            {"intent": "delete_file"},
        )

    def test_delete_folder(self):
        self.assertEqual(
            parse_intent("Remove folder"),
            {"intent": "delete_folder"},
        )

    def test_move_file(self):
        self.assertEqual(
            parse_intent("Move this file"),
            {"intent": "move_file"},
        )

    def test_exit_command(self):
        self.assertEqual(
            parse_intent("Goodbye"),
            {"intent": "exit"},
        )

    def test_unknown_command(self):
        self.assertEqual(
            parse_intent("Dance"),
            {"intent": "unknown"},
        )


    def test_empty_command(self):
        self.assertEqual(
            parse_intent(""),
            {"intent": "unknown"},
        )

    def test_whitespace_command(self):
        self.assertEqual(
            parse_intent("   "),
            {"intent": "unknown"},
        )

    def test_tanglish_open_chrome(self):
        self.assertEqual(
            parse_intent("Chrome open pannu"),
            {"intent": "open_chrome"},
        )

    def test_tanglish_open_downloads(self):
        self.assertEqual(
            parse_intent("Downloads folder-ah open pannu"),
            {"intent": "open_folder", "target": "downloads"},
        )

    def test_tanglish_open_website(self):
        self.assertEqual(
            parse_intent("YouTube website open pannu"),
            {"intent": "open_website", "target": "youtube"},
        )

    def test_tanglish_find_files(self):
        self.assertEqual(
            parse_intent("PDF files thedu"),
            {"intent": "find_files", "target": "pdf files"},
        )

    def test_tanglish_delete_file(self):
        self.assertEqual(
            parse_intent("File delete pannu"),
            {"intent": "delete_file"},
        )

    def test_tanglish_delete_folder(self):
        self.assertEqual(
            parse_intent("Folder delete pannu"),
            {"intent": "delete_folder"},
        )

    def test_tanglish_move_file(self):
        self.assertEqual(
            parse_intent("File move pannu"),
            {"intent": "move_file"},
        )

    def test_non_string_input(self):
        self.assertEqual(
            parse_intent(None),
            {"intent": "unknown"},
        )

    def test_invalid_and_unsupported_inputs(self):
        for value in (None, 12, "", "   ", "Dance!", "open settings"):
            with self.subTest(value=value):
                self.assertEqual(parse_intent(value), {"intent": "unknown"})

    def test_chrome_variants(self):
        for command in (
            "Open Chrome", "Launch Chrome", "Chrome open", "Chrome open pannu",
            "Chrome ah open pannu", "Open browser", "Browser open pannu",
        ):
            with self.subTest(command=command):
                self.assertEqual(parse_intent(command), {"intent": "open_chrome"})

    def test_approved_folder_variants_and_no_website_capture(self):
        cases = {
            "Open Downloads": "downloads",
            "Open Desktop": "desktop",
            "Open Documents": "documents",
            "Downloads folder-ah open pannu": "downloads",
            "Desktop open pannu": "desktop",
            "Documents folder open pannu": "documents",
            "Downloads thira": "downloads",
            "Open Downloads folder": "downloads",
        }
        for command, target in cases.items():
            with self.subTest(command=command):
                self.assertEqual(parse_intent(command), {"intent": "open_folder", "target": target})

    def test_website_variants_keep_explicit_target(self):
        cases = {
            "Open website https://example.com": "https://example.com",
            "Open site https://example.com": "https://example.com",
            "Visit https://example.com": "https://example.com",
            "YouTube website open pannu": "youtube",
            "YouTube open pannu": "youtube",
        }
        for command, target in cases.items():
            with self.subTest(command=command):
                self.assertEqual(parse_intent(command), {"intent": "open_website", "target": target})

    def test_file_search_variants_strip_command_suffix(self):
        cases = {
            "Search files report": "report",
            "PDF files thedu": "pdf files",
            "report file thedi": "report file",
            "report files kandu pidi": "report files",
        }
        for command, target in cases.items():
            with self.subTest(command=command):
                self.assertEqual(parse_intent(command), {"intent": "find_files", "target": target})

    def test_case_whitespace_and_punctuation(self):
        self.assertEqual(parse_intent("  dOwNLoAds   FOLDER-ah OPEN pannu!!"),
                         {"intent": "open_folder", "target": "downloads"})
        self.assertEqual(normalize_command("  Open   Chrome! "), "open chrome")

    def test_exit_tanglish_variants(self):
        for command in ("Exit", "Quit", "Goodbye", "Veliya po", "Niruthu"):
            with self.subTest(command=command):
                self.assertEqual(parse_intent(command), {"intent": "exit"})



if __name__ == "__main__":
    unittest.main()
