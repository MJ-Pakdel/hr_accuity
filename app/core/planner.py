import uuid
from typing import List, Tuple

from app.core.schemas import (
    AssessmentPlan,
    AssessmentRequest,
    PedagogicalStrategy,
    StudentProfile,
)

MIN_PROBLEMS = 5
MAX_PROBLEMS = 15


def generate_plan(profile: StudentProfile, request: AssessmentRequest) -> AssessmentPlan:
    """Very simple heuristic-based planner.

    In production this can be replaced with an LLM that returns the same JSON schema.
    """
    reasoning: List[str] = []
    reasoning.append(f"Strategy selected: {request.pedagogical_strategy}")

    # Decide on topics & difficulty range
    if request.pedagogical_strategy == PedagogicalStrategy.REVIEW:
        target_topics = profile.mastered_topics
        difficulty_range: Tuple[int, int] = (1, 2)
        num_problems = MIN_PROBLEMS
        reasoning.append("Reviewing previously mastered topics with low difficulty.")
    elif request.pedagogical_strategy == PedagogicalStrategy.NEW_TOPIC_INTRODUCTION:
        target_topics = profile.learning_goals
        difficulty_range = (1, 3)
        num_problems = MIN_PROBLEMS
        reasoning.append("Introducing new learning goals with gentle difficulty progression.")
    else:  # CHALLENGE
        target_topics = list(set(profile.mastered_topics + profile.learning_goals))
        difficulty_range = (3, 5)
        num_problems = MAX_PROBLEMS
        reasoning.append("Challenging student with a mix of mastered and goal topics at higher difficulty.")

    reasoning.append(f"Target topics: {target_topics}")
    reasoning.append(f"Difficulty range: {difficulty_range}")
    reasoning.append(f"Number of problems: {num_problems}")

    return AssessmentPlan(
        plan_id=str(uuid.uuid4()),
        target_topics=target_topics,
        num_problems=num_problems,
        difficulty_range=difficulty_range,
        reasoning_log=reasoning,
    ) 