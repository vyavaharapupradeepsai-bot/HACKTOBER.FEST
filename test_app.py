import json
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import app


class PublicDemoTests(unittest.TestCase):
    def _response(self):
        content = {
            "takeaways": ["First point", "Second point", "Third point"],
            "definitions": [{"term": "Variable", "definition": "A named value."}],
            "question": "What is a variable?",
            "answer": "A named value.",
        }
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content=json.dumps(content))
                )
            ]
        )

    def test_generates_markdown_with_hosted_model(self):
        with patch.dict(os.environ, {"HF_TOKEN": "test-token"}):
            with patch(
                "app.InferenceClient"
            ) as client_class:
                client_class.return_value.chat_completion.return_value = self._response()
                result = app.generate_web_cheatsheet("Notes about variables.")

        self.assertEqual(
            sum(line.startswith("- ") for line in result.splitlines()),
            3,
        )
        self.assertEqual(result.count("**Question:**"), 1)
        self.assertIn("## Key Definitions", result)
        client_class.assert_called_once_with(
            model=app.MODEL_ID,
            provider="featherless-ai",
            token="test-token",
            timeout=120,
        )

    def test_requires_notes(self):
        self.assertIn("paste your lecture notes", app.generate_web_cheatsheet(" "))

    def test_limits_notes_size(self):
        result = app.generate_web_cheatsheet("a" * (app.MAX_NOTES_LENGTH + 1))
        self.assertIn("20,000 characters", result)

    def test_missing_server_token_is_reported(self):
        with patch.dict(os.environ):
            os.environ.pop("HF_TOKEN", None)
            with patch("app.InferenceClient") as client_class:
                result = app.generate_web_cheatsheet("Sample lecture notes.")

        self.assertIn("not configured", result)
        client_class.assert_not_called()


if __name__ == "__main__":
    unittest.main()
