import uuid
from enum import Enum
from typing import List, Tuple, Dict
from pydantic import BaseModel


class PedagogicalStrategy(str, Enum):
    REVIEW = "REVIEW"
    NEW_TOPIC_INTRODUCTION = "NEW_TOPIC_INTRODUCTION"
    CHALLENGE = "CHALLENGE"


class StudentProfile(BaseModel):
    id: str
    mastered_topics: List[str]
    learning_goals: List[str]


class AssessmentRequest(BaseModel):
    max_total_time_minutes: int
    pedagogical_strategy: PedagogicalStrategy


class AssessmentPlan(BaseModel):
    plan_id: str
    target_topics: List[str]
    num_problems: int
    difficulty_range: Tuple[int, int]
    reasoning_log: List[str]


class MathProblem(BaseModel):
    id: str
    text: str
    topic: str
    difficulty: int  # 1 (easy) – 5 (hard)
    estimated_time_to_solve_minutes: int


class GeneratedAssessment(BaseModel):
    assessment_id: str
    selected_problems: List[MathProblem]
    total_estimated_time_minutes: int
    constraints: Dict[str, int]


class AssessmentGenerationResponse(BaseModel):
    assessment_id: str
    planner_output: Dict[str, object]
    executor_output: Dict[str, object] 