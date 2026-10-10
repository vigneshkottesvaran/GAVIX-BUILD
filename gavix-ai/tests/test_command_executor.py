import unittest
from pathlib import Path
from unittest.mock import patch

from src.core.command_executor import execute_command
from src.main import handle_command


class TestCommandExecutor(unittest.TestCase):
    def assert_result_shape(self, result):
        self.assertEqual(
            set(result),
            {"success", "intent", "message", "data", "needs_clarification"},
        )
        self.assertIsInstance(result["success"], bool)
        self.assertIsInstance(result["intent"], str)
        self.assertIsInstance(result["message"], str)

    @patch("src.core.command_executor.open_chrome", return_value=True)
    def test_open_chrome_dispatch(self, skill):
        result = execute_command("Launch Chrome")
        self.assert_result_shape(result)
        self.assertTrue(result["success"])
        self.assertEqual(result["intent"], "open_chrome")
        skill.assert_called_once_with()

    @patch("src.core.command_executor.open_website", return_value=True)
    def test_open_website_dispatch(self, skill):
        result = execute_command("Visit https://example.com")
        self.assert_result_shape(result)
        self.assertTrue(result["success"])
        skill.assert_called_once_with("https://example.com")

    @patch("src.core.command_executor.open_folder", return_value=True)
    def test_open_folder_dispatch(self, skill):
        result = execute_command("Downloads folder-ah open pannu")
        self.assertTrue(result["success"])
        self.assertEqual(result["data"], {"target": "downloads"})
        skill.assert_called_once_with("downloads")

    @patch("src.core.command_executor.find_files_module.find_files", return_value=[Path("report.pdf")])
    def test_find_files_dispatch(self, skill):
        result = execute_command("Find PDF files")
        self.assertTrue(result["success"])
        self.assertEqual(result["data"], {"files": ["report.pdf"]})
        skill.assert_called_once_with("pdf files", "downloads")

    def test_unknown_command_returns_standard_failure(self):
        result = execute_command("Dance")
        self.assert_result_shape(result)
        self.assertFalse(result["success"])
        self.assertEqual(result["intent"], "unknown")

    @patch("src.main.print")
    @patch("src.main.execute_command", return_value={
        "success": True,
        "intent": "open_folder",
        "message": "Opened downloads.",
        "data": {"target": "downloads"},
        "needs_clarification": False,
    })
    def test_main_displays_executor_result(self, execute, print_mock):
        result = handle_command("Open Downloads")
        execute.assert_called_once()
        self.assertEqual(result["intent"], "open_folder")
        print_mock.assert_called_once_with("GAVIX: Opened downloads.")

    def test_missing_targets_request_clarification(self):
        for command, intent, phrase in (
            ("Open website", "open_website", "Which website"),
            ("Find files", "find_files", "Which files"),
        ):
            with self.subTest(command=command):
                result = execute_command(command)
                self.assert_result_shape(result)
                self.assertFalse(result["success"])
                self.assertEqual(result["intent"], intent)
                self.assertTrue(result["needs_clarification"])
                self.assertIn(phrase, result["message"])

    @patch("src.core.command_executor.open_chrome", return_value=False)
    def test_skill_failure_is_not_reported_as_success(self, _skill):
        result = execute_command("Open Chrome")
        self.assertFalse(result["success"])
        self.assertIn("Could not", result["message"])

    @patch("src.core.command_executor.open_folder", side_effect=RuntimeError("internal detail"))
    def test_skill_exception_does_not_expose_traceback_or_exception(self, _skill):
        result = execute_command("Open Downloads")
        self.assert_result_shape(result)
        self.assertFalse(result["success"])
        self.assertNotIn("internal detail", result["message"])
        self.assertNotIn("Traceback", result["message"])

    @patch("src.core.command_executor.open_website", side_effect=ValueError("Only HTTP(S) is allowed."))
    def test_url_validation_failure_is_returned(self, skill):
        result = execute_command("YouTube open pannu")
        self.assertFalse(result["success"])
        self.assertEqual(result["message"], "Only HTTP(S) is allowed.")
        skill.assert_called_once_with("youtube")

    @patch("src.skills.open_browser.webbrowser.open")
    def test_invalid_url_never_reaches_browser(self, browser):
        result = execute_command("Open website javascript:alert(1)")
        self.assertFalse(result["success"])
        browser.assert_not_called()

    @patch("src.core.command_executor._run_move_file")
    @patch("src.core.command_executor.find_files_module.find_files")
    def test_move_cannot_be_bypassed_without_confirmation_input(self, find, move):
        result = execute_command("Move file")
        self.assertTrue(result["needs_clarification"])
        find.assert_not_called()
        move.assert_not_called()

    @patch("src.core.command_executor._run_move_file", return_value=True)
    @patch("src.core.command_executor.find_files_module.find_files", return_value=[Path("report.pdf")])
    def test_move_requires_exact_confirmation(self, find, move):
        answers = iter(("report", "1", "yes"))
        result = execute_command("Move file", input_fn=lambda _prompt: next(answers))
        self.assertFalse(result["success"])
        move.assert_not_called()

    @patch("src.core.command_executor._run_move_file", return_value=True)
    @patch("src.core.command_executor.find_files_module.find_files", return_value=[Path("report.pdf")])
    def test_confirmed_move_calls_guarded_skill(self, find, move):
        answers = iter(("report", "1", "CONFIRM"))
        result = execute_command("Move file", input_fn=lambda _prompt: next(answers))
        self.assertTrue(result["success"])
        move.assert_called_once_with("report.pdf", "documents", confirmed=True)

    @patch("src.core.command_executor._run_delete_file")
    def test_delete_file_cannot_be_bypassed_by_direct_call(self, delete):
        result = execute_command("Delete file")
        self.assertTrue(result["needs_clarification"])
        delete.assert_not_called()

    @patch("src.core.command_executor._run_delete_file", return_value=True)
    @patch("src.core.command_executor.find_files_module.find_files", return_value=[Path("report.pdf")])
    def test_confirmed_delete_calls_guarded_skill(self, find, delete):
        answers = iter(("report", "1", "CONFIRM"))
        result = execute_command("Delete file", input_fn=lambda _prompt: next(answers))
        self.assertTrue(result["success"])
        delete.assert_called_once_with("report.pdf", confirmed=True)

    @patch("src.core.command_executor._run_delete_folder")
    def test_delete_folder_cannot_be_bypassed_by_direct_call(self, delete):
        result = execute_command("Delete folder")
        self.assertTrue(result["needs_clarification"])
        delete.assert_not_called()

if __name__ == "__main__":
    unittest.main()
