
import unittest
from unittest.mock import patch

from src.skills.open_browser import open_website


class TestOpenWebsite(unittest.TestCase):

    @patch("src.skills.open_browser.webbrowser.open")
    def test_valid_https_url(self, mock_open):
        mock_open.return_value = True

        result = open_website("https://example.com")

        self.assertTrue(result)
        mock_open.assert_called_once_with("https://example.com")

    @patch("src.skills.open_browser.webbrowser.open")
    def test_valid_http_url(self, mock_open):
        mock_open.return_value = True

        result = open_website("http://example.com")

        self.assertTrue(result)
        mock_open.assert_called_once_with("http://example.com")

    @patch("src.skills.open_browser.webbrowser.open")
    def test_javascript_url_is_rejected(self, mock_open):
        with self.assertRaises(ValueError):
            open_website("javascript:alert(1)")

        mock_open.assert_not_called()

    @patch("src.skills.open_browser.webbrowser.open")
    def test_empty_url_is_rejected(self, mock_open):
        with self.assertRaises(ValueError):
            open_website("")

        mock_open.assert_not_called()

    @patch("src.skills.open_browser.webbrowser.open")
    def test_missing_domain_is_rejected(self, mock_open):
        with self.assertRaises(ValueError):
            open_website("https://")

        mock_open.assert_not_called()


if __name__ == "__main__":
    unittest.main()
