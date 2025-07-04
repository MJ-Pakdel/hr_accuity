from typing import List, Optional

from fastapi import APIRouter, HTTPException, Path, Query

from app.core.data import db
from app.core.schemas import MathProblem

router = APIRouter(prefix="/problems", tags=["problems"])


@router.get("", response_model=List[MathProblem])
async def list_problems(
    topic: Optional[str] = Query(None),
    difficulty: Optional[int] = Query(None, ge=1, le=5),
):
    """Return all problems, optionally filtered by topic and/or difficulty."""
    return db.list_problems(topic=topic, difficulty=difficulty)


@router.get("/{problem_id}", response_model=MathProblem)
async def get_problem(problem_id: str = Path(...)):
    problem = db.get_problem(problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem


@router.post("", response_model=MathProblem, status_code=201)
async def create_problem(problem: MathProblem):
    if db.get_problem(problem.id):
        raise HTTPException(status_code=400, detail="Problem ID already exists")
    db.add_problem(problem)
    return problem


@router.put("/{problem_id}", response_model=MathProblem)
async def update_problem(problem_id: str, problem: MathProblem):
    try:
        db.update_problem(problem_id, problem)
    except KeyError:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem


@router.delete("/{problem_id}", status_code=204)
async def delete_problem(problem_id: str):
    if not db.get_problem(problem_id):
        raise HTTPException(status_code=404, detail="Problem not found")
    db.delete_problem(problem_id) 