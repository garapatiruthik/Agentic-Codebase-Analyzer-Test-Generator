import sys
from pathlib import Path

import uvicorn

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from advanced_project.src.main import app


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
