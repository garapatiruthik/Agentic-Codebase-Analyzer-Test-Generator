from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, DirectoryPath, Field, field_validator

from .pipeline import run_full_research_pipeline

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

app = FastAPI(title="Codebase Researcher and Reporter", version="1.0.0")


class QueryRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    query: str = Field(min_length=1, max_length=2000)
    target_dir: DirectoryPath

    @field_validator("target_dir", mode="before")
    @classmethod
    def require_absolute_target_directory(cls, value):
        if isinstance(value, (str, Path)) and not Path(value).is_absolute():
            raise ValueError("target_dir must be an absolute path.")
        return value


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/run")
async def run_researcher(request: QueryRequest):
    report = await run_full_research_pipeline(
        user_query=request.query,
        target_directory=request.target_dir.resolve(),
    )
    return {"report": report}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
