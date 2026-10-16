
import argparse
from pathlib import Path
import ollama


def generate_cheatsheet(notes, model):
    prompt = f"""
You are an exam revision assistant.

Read the notes and use only information
supported by the notes. Do not invent facts.

Create these three sections in Markdown:

1. THREE CORE TAKEAWAYS
   Give exactly 3 short bullet points.

2. KEY DEFINITIONS
   Give important terms and definitions in a
   Markdown table with Term and Definition columns.

3. RAPID-FIRE QUIZ
   Give exactly one question based on the notes.
   Include its correct answer under an Answer heading.

Keep everything concise and useful for exams.

NOTES:
{notes}
"""

    response = ollama.chat(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response["message"]["content"]


def main():
    parser = argparse.ArgumentParser(
        description="Generate an exam cheat-sheet from notes."
    )

    parser.add_argument(
        "input_file",
        help="Path to your lecture notes text file"
    )

    parser.add_argument(
        "-o", "--output",
        default="cheatsheet.md",
        help="Output Markdown file"
    )

    parser.add_argument(
        "--model",
        default="gemma3:1b",
        help="Installed Ollama model name"
    )

    args = parser.parse_args()
    input_path = Path(args.input_file)

    if not input_path.is_file():
        parser.error(f"File not found: {input_path}")

    notes = input_path.read_text(
        encoding="utf-8"
    ).strip()

    if not notes:
        parser.error("The notes file is empty.")

    try:
        print("Generating your exam cheat-sheet...")

        result = generate_cheatsheet(
            notes, args.model
        )

        Path(args.output).write_text(
            result + "\n",
            encoding="utf-8"
        )

        print("Success! Cheat-sheet saved to:")
        print(args.output)

    except ollama.ResponseError as error:
        print(f"Ollama model error: {error}")
    except Exception as error:
        print(f"Error: {error}")
        print("Check Ollama and your model installation.")


if __name__ == "__main__":
    main()
