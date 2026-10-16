# Exam Cheat-Sheet Generator

A beginner-friendly Python CLI for solving **The Overwhelming Notes Trap**: turn a lecture-notes text file into a concise exam revision sheet using a model running locally with Ollama.

The generated Markdown contains exactly three core takeaways, a table of key definitions, and one rapid-fire question with its answer. The default output file is `cheatsheet.md`.

## What you need

- Python 3.9 or newer
- [Ollama](https://ollama.com/) installed and running
- Enough local disk space and memory for the model

## Install

Run these commands from this project folder. The first installs the Python Ollama client listed in `requirements.txt`:

```powershell
python -m pip install -r requirements.txt
```

First open Ollama so its local service is running. This command downloads the default `gemma3:1b` model; you only need to do this once:

```bash
ollama pull gemma3:1b
```

## Generate a cheat-sheet

Ollama must be running while the program generates a sheet. If the Ollama app is not already running, start the local Ollama server in a separate terminal:

```powershell
ollama serve
```

Keep that terminal open. In another terminal, run this command from the project folder. It reads the sample `notes.txt` and writes `cheatsheet.md`:

```powershell
python main.py notes.txt
```

To use a different model already downloaded in Ollama, add `--model MODEL_NAME`. To save to a different file, add `--output FILE_NAME`:

```powershell
python main.py notes.txt --model gemma3:1b --output review.md
```

The program reports a helpful message if the notes file is missing or empty, Ollama is not running, or the requested model is not installed. Download another model with `ollama pull MODEL_NAME`.

## Test

This runs the built-in offline tests. Ollama does not need to be running because the tests use a mock response:

```powershell
python -m unittest -v
```

## Push changes to GitHub

Run these commands from this project folder. First, check which files have changed so you can confirm what will be included:

```powershell
git status
```

This stages only the project files and tests, rather than unrelated files elsewhere on your computer:

```powershell
git add .gitignore main.py requirements.txt README.md notes.txt cheatsheet.md test_main.py
```

This saves the staged changes in a local commit with a descriptive message:

```powershell
git commit -m "Improve exam cheat-sheet generator"
```

This sends the `main` branch to the configured GitHub remote named `origin`:

```powershell
git push origin main
```
