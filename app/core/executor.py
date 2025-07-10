import uuid
import asyncio
from typing import List

from app.core.data import db
from app.core.schemas import AssessmentPlan, GeneratedAssessment, MathProblem


async def execute_plan(plan: AssessmentPlan, max_total_time_minutes: int) -> GeneratedAssessment:
    """Retrieve problems that satisfy the plan while respecting the time constraint."""
    # Gather candidate problems by topic
    candidates: List[MathProblem] = []

    # Fetch each topic's problems concurrently
    fetch_tasks = [db.list_problems(topic=topic) for topic in plan.target_topics]
    topic_problem_lists = await asyncio.gather(*fetch_tasks)
    for plist in topic_problem_lists:
        candidates.extend(plist)

    # Filter by difficulty
    low, high = plan.difficulty_range
    candidates = [p for p in candidates if low <= p.difficulty <= high]

    # De-duplicate while preserving order
    seen = set()
    unique_candidates: List[MathProblem] = []
    for p in candidates:
        if p.id not in seen:
            unique_candidates.append(p)
            seen.add(p.id)

    # Sort (optional): easiest first
    unique_candidates.sort(key=lambda p: p.difficulty)

    selected: List[MathProblem] = []
    total_time = 0
    for problem in unique_candidates:
        if len(selected) >= plan.num_problems:
            break
        if total_time + problem.estimated_time_to_solve_minutes > max_total_time_minutes:
            break
        selected.append(problem)
        total_time += problem.estimated_time_to_solve_minutes

    return GeneratedAssessment(
        assessment_id=str(uuid.uuid4()),
        selected_problems=selected,
        total_estimated_time_minutes=total_time,
        constraints={"max_total_time_minutes": max_total_time_minutes},
    ) 