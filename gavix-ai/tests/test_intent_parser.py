
import unittest

from src.core.intent_parser import parse_intent


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


if __name__ == "__main__":
    unittest.main()
