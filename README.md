# Exam Cheat-Sheet Generator

A Python command-line tool that uses a local Ollama model to convert lecture notes into concise exam revision material.

## Features
- Generates exactly 3 core takeaways
- Extracts key definitions
- Creates one rapid-fire quiz question with its answer

## Requirements
- Python
- Ollama
- Gemma model

## Setup

Install the Python package:

```bash
python -m pip install -r requirements.txt
```

Download the model:

```bash
ollama pull gemma3:1b
```

## Run

Keep Ollama running, then execute:

```bash
python main.py notes.txt
```

The generated cheat-sheet is saved as `cheatsheet.md`.

## License
MIT