from fastapi import FastAPI
from .db import Base, engine
from .routers import uploads, evaluate, search

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Automated Resume Relevance Check System")

app.include_router(uploads.router)
app.include_router(evaluate.router)
app.include_router(search.router)

@app.get("/")
def health():
    return {"status": "ok"}
