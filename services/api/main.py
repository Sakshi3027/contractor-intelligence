import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import leads, outreach, analytics, model

app = FastAPI(
    title="Contractor Intelligence API",
    description="Agentic lead intelligence system for IT contractor partners",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(leads.router)
app.include_router(outreach.router)
app.include_router(analytics.router)
app.include_router(model.router)


@app.get("/")
def root():
    return {
        "name": "Contractor Intelligence API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0",
                port=8000, reload=True)