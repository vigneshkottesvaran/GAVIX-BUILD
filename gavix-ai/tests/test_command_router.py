
import unittest

from src.core.command_router import route_command


class TestCommandRouter(unittest.TestCase):

    def test_chrome_routes_to_browser(self):
        result = route_command("Launch Chrome")
        self.assertEqual(result["intent"], "open_chrome")
        self.assertEqual(result["skill"], "open_browser")

    def test_website_routes_to_browser(self):
        result = route_command("Visit https://example.com")
        self.assertEqual(result["intent"], "open_website")
        self.assertEqual(result["skill"], "open_browser")
        self.assertEqual(result["target"], "https://example.com")

    def test_downloads_routes_to_folder_skill(self):
        result = route_command("Open Downloads")
        self.assertEqual(result["skill"], "open_folder")
        self.assertEqual(result["target"], "downloads")

    def test_tanglish_downloads_routes_to_folder_skill(self):
        result = route_command("Downloads folder-ah open pannu")
        self.assertEqual(result["intent"], "open_folder")
        self.assertEqual(result["skill"], "open_folder")
        self.assertEqual(result["target"], "downloads")

    def test_tanglish_website_routes_to_browser(self):
        result = route_command("YouTube website open pannu")
        self.assertEqual(result["intent"], "open_website")
        self.assertEqual(result["skill"], "open_browser")
        self.assertEqual(result["target"], "youtube")

    def test_search_routes_to_find_files(self):
        result = route_command("Find PDF files")
        self.assertEqual(result["skill"], "find_files")
        self.assertEqual(result["target"], "pdf files")

    def test_move_routes_to_move_skill(self):
        result = route_command("Move this file")
        self.assertEqual(result["skill"], "move_file")

    def test_delete_file_routes_correctly(self):
        result = route_command("Delete file")
        self.assertEqual(result["skill"], "delete_file")

    def test_delete_folder_routes_correctly(self):
        result = route_command("Delete folder")
        self.assertEqual(result["skill"], "delete_folder")

    def test_goodbye_routes_to_exit(self):
        result = route_command("Goodbye")
        self.assertEqual(result["skill"], "exit")

    def test_unknown_command_has_no_skill(self):
        result = route_command("Dance")
        self.assertEqual(result["intent"], "unknown")
        self.assertIsNone(result["skill"])


if __name__ == "__main__":
    unittest.main()
