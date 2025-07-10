import uuid
import os
import sys
from pathlib import Path

# Ensure the project root (hr_accuity) is on sys.path so `import app` works when tests are run from repo root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest

from app.core.schemas import AssessmentPlan, MathProblem
from app.core.executor import execute_plan


@pytest.fixture()
def sample_problems():
    """Create a deterministic list of problems across two topics with varying difficulty/time."""
    problems = []
    for idx, (topic, difficulty, minutes) in enumerate(
        [
            ("Basic Arithmetic", 1, 1),
            ("Basic Arithmetic", 2, 2),
            ("Fractions", 2, 2),
            ("Fractions", 3, 3),
            ("Fractions", 4, 4),
            ("Introduction to Algebra", 3, 3),
        ]
    ):
        problems.append(
            MathProblem(
                id=str(idx),
                text=f"Problem {idx}",
                topic=topic,
                difficulty=difficulty,
                estimated_time_to_solve_minutes=minutes,
            )
        )
    return problems


@pytest.fixture()
def monkeypatch_db(monkeypatch, sample_problems):
    """Patch the ProblemDatabase.list_problems to return our sample problems filtered by topic."""

    async def fake_list_problems(topic=None, difficulty=None):
        items = sample_problems
        if topic is not None:
            items = [p for p in items if p.topic == topic]
        if difficulty is not None:
            items = [p for p in items if p.difficulty == difficulty]
        return items
    # Apply patch
    from app.core import data

    monkeypatch.setattr(data.db, "list_problems", fake_list_problems)


def _make_plan(num_problems=4, difficulty_range=(1, 3)):
    return AssessmentPlan(
        plan_id=str(uuid.uuid4()),
        target_topics=["Basic Arithmetic", "Fractions"],
        num_problems=num_problems,
        difficulty_range=difficulty_range,
        reasoning_log=[],
    )


@pytest.mark.asyncio
async def test_execute_plan_respects_constraints(monkeypatch_db):
    plan = _make_plan(num_problems=3, difficulty_range=(1, 3))
    max_time = 5  # minutes

    assessment = await execute_plan(plan, max_time)

    # Verify number of problems <= requested
    assert len(assessment.selected_problems) <= plan.num_problems

    # Verify difficulty range
    low, high = plan.difficulty_range
    assert all(low <= p.difficulty <= high for p in assessment.selected_problems)

    # Verify total time constraint
    assert assessment.total_estimated_time_minutes <= max_time

    # Verify computed time equals sum of selected problems
    assert assessment.total_estimated_time_minutes == sum(
        p.estimated_time_to_solve_minutes for p in assessment.selected_problems
    )


@pytest.mark.asyncio
async def test_execute_plan_returns_unique_problems(monkeypatch_db):
    plan = _make_plan(num_problems=10, difficulty_range=(1, 4))
    assessment = await execute_plan(plan, max_total_time_minutes=100)

    ids = [p.id for p in assessment.selected_problems]
    assert len(ids) == len(set(ids))  # no duplicates 