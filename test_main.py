import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch

import ollama

import main


class ExamCheatSheetTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.notes_file = Path(self.temp_dir.name) / "notes.txt"
        self.notes_file.write_text("A variable stores a value.", encoding="utf-8")

    def _response(self, takeaways=None):
        content = {
            "takeaways": takeaways or [
                "A variable stores a value.",
                "Python has several data types.",
                "A loop repeats a block of code.",
            ],
            "definitions": [
                {"term": "Variable", "definition": "A name for a value."},
                {"term": "Type|kind", "definition": "A category\nof value."},
            ],
            "question": "What does a variable store?",
            "answer": "A value.",
        }
        return {"message": {"content": json.dumps(content)}}

    def _run_cli(self, *arguments):
        with patch("sys.argv", ["main.py", str(self.notes_file), *arguments]):
            return main.main()

    def test_generates_exact_sections_and_default_output(self):
        original_directory = Path.cwd()
        os.chdir(self.temp_dir.name)
        self.addCleanup(os.chdir, original_directory)

        with patch("main.ollama.chat", return_value=self._response()) as chat:
            self.assertEqual(self._run_cli(), 0)

        chat.assert_called_once()
        self.assertEqual(chat.call_args.kwargs["model"], "gemma3:1b")
        content = (Path(self.temp_dir.name) / "cheatsheet.md").read_text(
            encoding="utf-8"
        )
        self.assertEqual(
            sum(line.startswith("- ") for line in content.splitlines()),
            3,
        )
        self.assertEqual(content.count("**Question:**"), 1)
        self.assertEqual(content.count("**Answer:**"), 1)
        self.assertIn("| Type\\|kind | A category of value. |", content)

    def test_missing_notes_file_is_reported(self):
        with patch("sys.argv", ["main.py", str(self.notes_file) + ".missing"]):
            with redirect_stderr(io.StringIO()) as error:
                with self.assertRaises(SystemExit) as result:
                    main.main()

        self.assertEqual(result.exception.code, 2)
        self.assertIn("File not found", error.getvalue())

    def test_empty_notes_file_is_reported(self):
        self.notes_file.write_text("  \n", encoding="utf-8")
        with redirect_stderr(io.StringIO()) as error:
            with self.assertRaises(SystemExit) as result:
                self._run_cli()

        self.assertEqual(result.exception.code, 2)
        self.assertIn("notes file is empty", error.getvalue())

    def test_ollama_connection_failure_is_reported(self):
        with patch(
            "main.ollama.chat",
            side_effect=ollama.RequestError("connection refused"),
        ):
            with redirect_stderr(io.StringIO()) as error:
                self.assertEqual(self._run_cli(), 1)

        self.assertIn("Could not connect to Ollama", error.getvalue())

    def test_missing_model_is_reported(self):
        with patch(
            "main.ollama.chat",
            side_effect=ollama.ResponseError("model not found", status_code=404),
        ):
            with redirect_stderr(io.StringIO()) as error:
                self.assertEqual(self._run_cli(), 1)

        self.assertIn("ollama pull gemma3:1b", error.getvalue())

    def test_invalid_model_output_is_not_saved(self):
        with patch(
            "main.ollama.chat",
            return_value=self._response(takeaways=["Only one takeaway."]),
        ):
            with redirect_stderr(io.StringIO()) as error:
                self.assertEqual(
                    self._run_cli("--output", str(Path(self.temp_dir.name) / "out.md")),
                    1,
                )

        self.assertIn("exactly 3 non-empty takeaways", error.getvalue())
        self.assertFalse((Path(self.temp_dir.name) / "out.md").exists())


if __name__ == "__main__":
    unittest.main()
