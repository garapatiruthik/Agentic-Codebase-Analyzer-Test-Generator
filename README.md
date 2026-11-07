# Reporter Project

The supported application is in `advanced_project`. It uses agentic AI to inspect a
local codebase, report evidence-based findings, and produce prioritized,
code-ready automated test cases. Proposed tests are reported, not executed or written
into the audited project.

The top-level `main.py`, `src.main`, and `Langchain\app.py` are compatibility entry
points for the same API. `Langchain\my_target_project` is an earlier sample project.

## Setup (Windows PowerShell)

Requirements: Python 3.11+, Node.js/npm, and a Groq API key. Create a fresh virtual
environment (the existing `.venv` may point to a Python installation that is no
longer present):

```powershell
py -m venv .venv-reporter
.\.venv-reporter\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
node --version
npm --version
```

Set `GROQ_API_KEY` in `advanced_project\.env` or in the process environment. Keep
the key private and do not commit `.env` files.

## Run

From the repository root:

```powershell
python main.py
```

The API listens on `127.0.0.1:8000`. Check `http://127.0.0.1:8000/health` or open
`http://127.0.0.1:8000/docs`. To analyze a codebase, POST to `/run` with `query` and
an absolute `target_dir`:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/run" `
  -H "Content-Type: application/json" `
  -d '{"query":"Review correctness, reliability, and security; propose tests.","target_dir":"C:\\path\\to\\project"}'
```

The response contains a Markdown report. Filesystem access is read-only and limited
to the requested directory; credentials, datasets, and generated/vendor directories
are excluded.

## Verify

From the repository root:

```powershell
python -m pytest advanced_project\tests
```

These focused tests do not need a Groq key or Node.js. A real research request needs
both and makes external model calls.