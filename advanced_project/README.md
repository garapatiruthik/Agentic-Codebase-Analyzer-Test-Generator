# Codebase Researcher and Reporter

This FastAPI service uses a Groq language model and a filesystem MCP server to
research a local codebase, produce an evidence-based Markdown report, and propose
prioritized automated test cases. The report describes tests to implement; it does
not execute or write code into the audited project.

## Requirements

- Python 3.11 or newer
- Node.js and npm (the filesystem MCP server is launched with `npx`)
- A Groq API key

Install dependencies from this directory:

```powershell
python -m pip install -r requirements.txt
```

Set `GROQ_API_KEY` in this directory's `.env` file or in the process environment.
Keep `.env` private; do not commit it. The API binds to `127.0.0.1` by default.

## Run

From `advanced_project`:

```powershell
python -m uvicorn src.main:app --host 127.0.0.1 --port 8000
```

Alternatively, run `python app.py`. Open `http://127.0.0.1:8000/docs` to explore
the API. `GET /health` checks that the service is running.

Send a request with an absolute path to the codebase to analyze:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/run" `
  -H "Content-Type: application/json" `
  -d '{"query":"Review correctness, reliability, and security; propose tests.","target_dir":"C:\\path\\to\\project"}'
```

The response is `{"report":"..."}`. The MCP filesystem server is restricted to the
requested directory, and the agent is limited to read-only listing and source/config
file reading. Credential files, data files, and generated/vendor directories are
excluded.

## Tests

From `advanced_project`:

```powershell
python -m pytest
```

These tests cover request validation, API behavior, and filesystem-tool restrictions.
They do not require a Groq API key or make external model calls.
