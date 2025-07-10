import json
import os
import asyncio
from typing import Dict, List, Optional

from app.core.schemas import MathProblem


class ProblemDatabase:
    """Thread-safe JSON file backed store. For production swap with real DB."""

    def __init__(self, filepath: str = "ProblemSet.json"):
        # Instantiate an asyncio lock tied to the current loop context when the DB is created.
        self._lock: asyncio.Lock = asyncio.Lock()
        self.filepath = os.path.abspath(filepath)
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w") as f:
                json.dump([], f)
        self._load()

    def _load(self):
        with open(self.filepath, "r") as f:
            data = json.load(f)
            self._problems: Dict[str, MathProblem] = {p["id"]: MathProblem(**p) for p in data}

    def _write(self):
        with open(self.filepath, "w") as f:
            json.dump([p.model_dump() for p in self._problems.values()], f, indent=2)

    # CRUD helpers
    async def list_problems(self, topic: Optional[str] = None, difficulty: Optional[int] = None) -> List[MathProblem]:
        # Pure in-memory lookup – safe to run directly
        problems = list(self._problems.values())
        if topic is not None:
            problems = [p for p in problems if p.topic == topic]
        if difficulty is not None:
            problems = [p for p in problems if p.difficulty == difficulty]
        return problems

    async def get_problem(self, problem_id: str) -> Optional[MathProblem]:
        return self._problems.get(problem_id)

    async def add_problem(self, problem: MathProblem):
        async with self._lock:
            self._problems[problem.id] = problem
            await asyncio.to_thread(self._write)

    async def update_problem(self, problem_id: str, problem: MathProblem):
        async with self._lock:
            if problem_id not in self._problems:
                raise KeyError("Problem not found")
            self._problems[problem_id] = problem
            await asyncio.to_thread(self._write)

    async def delete_problem(self, problem_id: str):
        async with self._lock:
            if problem_id in self._problems:
                del self._problems[problem_id]
                await asyncio.to_thread(self._write)


db = ProblemDatabase() 