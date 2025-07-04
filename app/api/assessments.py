from fastapi import APIRouter

from app.core.executor import execute_plan
from app.core.planner import generate_plan
from app.core.schemas import (
    AssessmentGenerationResponse,
    AssessmentRequest,
    StudentProfile,
)

router = APIRouter(tags=["assessments"])


@router.post("/generate", response_model=AssessmentGenerationResponse)
async def generate_assessment(
    student_profile: StudentProfile, assessment_request: AssessmentRequest
):
    """High-level orchestration endpoint."""
    plan = generate_plan(student_profile, assessment_request)
    assessment = execute_plan(plan, assessment_request.max_total_time_minutes)

    return {
        "assessment_id": assessment.assessment_id,
        "planner_output": {
            "reasoning_log": plan.reasoning_log,
            "assessment_plan": plan.model_dump(),
        },
        "executor_output": {
            "selected_problems": [p.model_dump() for p in assessment.selected_problems],
            "total_estimated_time_minutes": assessment.total_estimated_time_minutes,
            "constraints": assessment.constraints,
        },
    } 