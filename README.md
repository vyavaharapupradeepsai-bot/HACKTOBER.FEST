---
title: Exam Cheat-Sheet Generator
emoji: 📝
colorFrom: blue
colorTo: indigo
sdk: gradio
app_file: app.py
python_version: "3.11"
---

# Exam Cheat-Sheet Generator

A beginner-friendly project for solving **The Overwhelming Notes Trap**: turn lecture notes into a concise exam revision sheet. Use the local Python CLI with Ollama, or deploy the Gradio web app on Hugging Face Spaces for a public demo.

The generated Markdown contains exactly three core takeaways, a table of key definitions, and one rapid-fire question with its answer. The default output file is `cheatsheet.md`.

## What you need

- Python 3.10 or newer
- [Ollama](https://ollama.com/) installed and running
- Or a Hugging Face account and Inference Providers access for the hosted web app

## Install

Run this command from the project folder to install the CLI and web-app dependencies:

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

## Public web demo (Hugging Face Spaces)

The web app uses the hosted `Qwen/Qwen2.5-3B-Instruct` model through Hugging Face Inference Providers. Unlike the CLI, the public web app does not need Ollama. Model availability and inference-provider usage limits or charges depend on your Hugging Face account.

1. Create a **public Gradio Space** named `exam-cheatsheet-generator` at [huggingface.co/new-space](https://huggingface.co/new-space).
2. Create a Hugging Face **fine-grained access token** that can make calls to Inference Providers. Do not paste the token into this repository.
3. In the Space's **Settings → Variables and secrets**, add a secret named `HF_TOKEN` and paste the token there. The app reads it on the server; it is never sent to visitors' browsers.
4. From this project folder, run the commands below. The login command authenticates the Hugging Face CLI (enter your token only when its prompt asks). The next command adds the Space as a separate Git remote, and the last publishes the project to that Space:

```powershell
hf auth login
git remote add huggingface https://huggingface.co/spaces/YOUR_HF_USERNAME/exam-cheatsheet-generator
git push huggingface main
```

Replace `YOUR_HF_USERNAME` with your Hugging Face account name. After the Space finishes building, its public URL will be:

```text
https://YOUR_HF_USERNAME-exam-cheatsheet-generator.hf.space
```

Visitors' notes are sent to the hosted model provider to generate a cheat-sheet. The demo limits notes to 20,000 characters and asks visitors not to submit private information.

## Test

This runs the built-in offline tests. Neither Ollama nor a Hugging Face token is needed because the tests use mock model responses:

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
git add .gitignore app.py main.py requirements.txt README.md notes.txt cheatsheet.md test_main.py test_app.py
```

This saves the staged changes in a local commit with a descriptive message:

```powershell
git commit -m "Improve exam cheat-sheet generator"
```

This sends the `main` branch to the configured GitHub remote named `origin`:

```powershell
git push origin main
```
