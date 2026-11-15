# vw-automotive-ai-agent
AI-powered agent for automated discovery, analysis, and tracking of automotive modifications and products across online sources. Includes structured data management, change detection, and weekly reporting.

## Prerequisites

Before you start, make sure the following is installed on your machine:
- **Python 3.14** (check with `python --version`)
- **Git**
- **Visual Studio Code** with the **Python** extension by Microsoft
- **Ollama** to run the language model locally: https://ollama.com
  After installing Ollama, download the model used by the agent:
  ```
  ollama pull qwen3:8b
  ```
  Ollama runs in the background on `http://localhost:11434`. The model and
  address can be changed in `config.yaml`.

## Installation

1. Clone the repository and open the folder:
   ```
   git clone https://github.com/Ali02434/vw-automotive-ai-agent.git
   cd vw-automotive-ai-agent
   ```

2. Create a virtual environment:
   ```
   python -m venv .venv
   ```

3. Activate it:
   - Windows (PowerShell):
     ```
     .venv\Scripts\Activate.ps1
     ```
     If you get an error that running scripts is disabled, run this once and try again:
     ```
     Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
     ```
   - macOS / Linux:
     ```
     source .venv/bin/activate
     ```
   You will see `(.venv)` at the start of the terminal line when it is active.

4. Install the dependencies:
   ```
   python -m pip install -r requirements.txt
   ```

5. In VS Code, select the interpreter from `.venv`:
   `Ctrl+Shift+P` → **Python: Select Interpreter** → choose the entry with `.venv`.

## Usage

Make sure Ollama is running, then start a search run in one of two ways:

- **In VS Code:** open **Run and Debug**, select **Suchlauf starten** and click ▶.
- **In the terminal** (with `.venv` active):
  ```
  python main.py
  ```

All settings are stored in `config.yaml`:

| Setting | Description |
|---|---|
| `limit` | Maximum number of search results per run |
| `llm.model` | Ollama model used for extraction |
| `llm.url` | Address of the Ollama server |
| `shops` | Online shops the agent searches |
| `areas` | Vehicle areas used for classification |

## Project structure

```
vw-automotive-ai-agent/
├── main.py            # Entry point: starts a search run
├── config.yaml        # Settings (limit, model, shops, areas)
├── requirements.txt   # Python dependencies
├── agent/
│   ├── settings.py    # Loads config.yaml
│   ├── database.py    # SQLite database  
│   ├── shops.py       # Fetches shop pages 
│   ├── llm.py         # Extraction with the local LLM 
│   └── report.py      # Delta report 
├── data/              # Local database files (not committed)
└── .vscode/
    └── launch.json    # "Suchlauf starten" run configuration
```

## Team

- Franco Reque Ucancial
- Ali Sener
- Halil Yesilöz

Project with Companies, Leibniz Universität Hannover