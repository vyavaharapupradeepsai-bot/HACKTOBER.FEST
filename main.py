import argparse
import json
import sys
from pathlib import Path

import ollama


CHEATSHEET_FORMAT = {
    "type": "object",
    "properties": {
        "takeaways": {
            "type": "array",
            "items": {"type": "string"},
        },
        "definitions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "term": {"type": "string"},
                    "definition": {"type": "string"},
                },
                "required": ["term", "definition"],
            },
        },
        "question": {"type": "string"},
        "answer": {"type": "string"},
    },
    "required": ["takeaways", "definitions", "question", "answer"],
}


def generate_cheatsheet(notes, model):
    prompt = f"""
Create a concise exam cheat-sheet using only facts in the notes.
Return JSON with exactly these keys:
- "takeaways": exactly 3 short strings
- "definitions": a list of objects with "term" and "definition" strings
- "question": exactly 1 rapid-fire question as a string
- "answer": the correct answer to that question as a string

NOTES:
{notes}
"""

    response = ollama.chat(
        model=model,
        format=CHEATSHEET_FORMAT,
        messages=[{"role": "user", "content": prompt}],
    )
    return format_cheatsheet(json.loads(response["message"]["content"]))


def format_cheatsheet(result):
    if not isinstance(result, dict):
        raise ValueError("the response must be a JSON object")

    takeaways = result.get("takeaways")
    definitions = result.get("definitions")
    question = result.get("question")
    answer = result.get("answer")

    if (
        not isinstance(takeaways, list)
        or len(takeaways) != 3
        or not all(isinstance(item, str) and item.strip() for item in takeaways)
    ):
        raise ValueError("the response must contain exactly 3 non-empty takeaways")

    if not isinstance(definitions, list):
        raise ValueError("the response definitions must be a list")

    for definition in definitions:
        if (
            not isinstance(definition, dict)
            or not isinstance(definition.get("term"), str)
            or not definition["term"].strip()
            or not isinstance(definition.get("definition"), str)
            or not definition["definition"].strip()
        ):
            raise ValueError("each definition must have a non-empty term and definition")

    if not isinstance(question, str) or not question.strip():
        raise ValueError("the response must contain one non-empty quiz question")
    if not isinstance(answer, str) or not answer.strip():
        raise ValueError("the response must contain a non-empty answer")

    lines = [
        "# Exam Cheat-Sheet",
        "",
        "## Three Core Takeaways",
        "",
    ]
    lines.extend(f"- {_single_line(item)}" for item in takeaways)
    lines.extend(
        [
            "",
            "## Key Definitions",
            "",
            "| Term | Definition |",
            "| --- | --- |",
        ]
    )
    lines.extend(
        f"| {_table_cell(item['term'])} | {_table_cell(item['definition'])} |"
        for item in definitions
    )
    lines.extend(
        [
            "",
            "## Rapid-Fire Quiz",
            "",
            f"**Question:** {_single_line(question)}",
            "",
            f"**Answer:** {_single_line(answer)}",
            "",
        ]
    )
    return "\n".join(lines)


def _single_line(text):
    return " ".join(text.split())


def _table_cell(text):
    return _single_line(text).replace("|", r"\|")


def main():
    parser = argparse.ArgumentParser(
        description="Generate an exam cheat-sheet from lecture notes using Ollama."
    )
    parser.add_argument("input_file", help="Path to your lecture notes text file")
    parser.add_argument(
        "-o",
        "--output",
        default="cheatsheet.md",
        help="Output Markdown file (default: cheatsheet.md)",
    )
    parser.add_argument(
        "--model",
        default="gemma3:1b",
        help="Installed Ollama model name (default: gemma3:1b)",
    )
    args = parser.parse_args()

    if not args.model.strip():
        parser.error("--model cannot be empty.")

    input_path = Path(args.input_file)
    if not input_path.is_file():
        parser.error(f"File not found: {input_path}")

    try:
        notes = input_path.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeDecodeError) as error:
        parser.error(f"Could not read {input_path}: {error}")

    if not notes:
        parser.error("The notes file is empty.")

    try:
        print("Generating your exam cheat-sheet...")
        result = generate_cheatsheet(notes, args.model)
        Path(args.output).write_text(result, encoding="utf-8")
    except ollama.RequestError as error:
        print(
            f"Could not connect to Ollama: {error}\n"
            "Start Ollama and try again.",
            file=sys.stderr,
        )
        return 1
    except ollama.ResponseError as error:
        if error.status_code == 404:
            message = (
                f"Ollama model '{args.model}' was not found. "
                f"Download it with: ollama pull {args.model}"
            )
        else:
            message = f"Ollama returned an error: {error}"
        print(message, file=sys.stderr)
        return 1
    except ValueError as error:
        print(f"Could not create the cheat-sheet: {error}", file=sys.stderr)
        return 1
    except OSError as error:
        print(
            f"Could not write output file '{args.output}': {error}",
            file=sys.stderr,
        )
        return 1

    print(f"Success! Cheat-sheet saved to: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
