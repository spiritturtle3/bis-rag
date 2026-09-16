from fastapi import FastAPI

from app.api import router


app = FastAPI(
    title="BIS RAG API",
    description=(
        "AI-powered recommendation engine for "
        "identifying applicable Indian Standards "
        "for procurement specifications."
    ),
    version="0.1.0",
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "BIS RAG API is running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }