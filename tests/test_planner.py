import pytest
import os
import sys
from pathlib import Path

# Ensure the project root (hr_accuity) is on sys.path so `import app` works when tests are run from repo root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core import planner
from app.core.schemas import AssessmentRequest, StudentProfile, PedagogicalStrategy


@pytest.fixture()
def sample_profile():
    return StudentProfile(
        id="student-1",
        mastered_topics=["Basic Arithmetic", "Fractions"],
        learning_goals=["Introduction to Algebra", "Geometry Fundamentals"],
    )


@pytest.mark.parametrize(
    "strategy,expected_topics,expected_range,expected_count",
    [
        (
            PedagogicalStrategy.REVIEW,
            ["Basic Arithmetic", "Fractions"],
            (1, 2),
            planner.MIN_PROBLEMS,
        ),
        (
            PedagogicalStrategy.NEW_TOPIC_INTRODUCTION,
            ["Introduction to Algebra", "Geometry Fundamentals"],
            (1, 3),
            planner.MIN_PROBLEMS,
        ),
        (
            PedagogicalStrategy.CHALLENGE,
            [
                "Basic Arithmetic",
                "Fractions",
                "Introduction to Algebra",
                "Geometry Fundamentals",
            ],
            (3, 5),
            planner.MAX_PROBLEMS,
        ),
    ],
)
@pytest.mark.asyncio
async def test_generate_plan(strategy, expected_topics, expected_range, expected_count, sample_profile):
    request = AssessmentRequest(max_total_time_minutes=30, pedagogical_strategy=strategy)

    plan = await planner.generate_plan(sample_profile, request)

    # Topics (order may vary for CHALLENGE so compare sets)
    assert set(plan.target_topics) == set(expected_topics)
    assert plan.difficulty_range == expected_range
    assert plan.num_problems == expected_count
    # Plan ID should be a valid UUID string
    import uuid

    uuid.UUID(plan.plan_id)  # Will raise ValueError if invalid

    # Reasoning log should not be empty
    assert len(plan.reasoning_log) > 0 