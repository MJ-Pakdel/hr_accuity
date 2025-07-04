from fastapi import FastAPI
from app.api.problems import router as problems_router
from app.api.assessments import router as assessments_router

app = FastAPI(
    title="Adaptive Learning Orchestrator API",
    version="0.1.0",
    description="Service for generating adaptive math assessments."
)

app.include_router(problems_router, prefix="/api")
app.include_router(assessments_router, prefix="/api/assessments")


@app.get("/") # health-check of the service and not the business logic
def read_root():
    """Health-check endpoint."""
    return {"status": "up"} 