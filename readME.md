# Adaptive Learning Orchestrator – Reference Implementation

This repository contains a minimal yet fully functional implementation of the **Assessment Generation Service** described in the take-home assignment.

---
## 1. High-Level Flow
1. Client calls `POST /api/assessments/generate` with a `student_profile` and an `assessment_request`.
2. The service invokes the **Planner** which converts the high-level request into a concrete `AssessmentPlan` (think/"reason" phase).
3. The **Executor** receives the plan and interacts with the problem database to build the actual assessment (act phase).
4. The combined result (plan + generated assessment) is returned to the client.

A full set of CRUD endpoints (`/api/problems`) allows administrators to manage the problem bank stored in `ProblemSet.json`.

---
## 2. Decoupled Components
| Component | Responsibility | Swappable? |
|-----------|---------------|------------|
| **Planner** (`app/core/planner.py`) | Analyses the request and decides *what* should be done (topics, difficulty, number of problems). | Yes – replace heuristics with a prompt to GPT-4 or a fine-tuned model without touching the Executor. |
| **Executor** (`app/core/executor.py`) | Executes the plan verbatim, fetching problems and assembling the assessment. | Yes – replace with smarter retrieval logic or a tool-using agent. |

### 2.1 Contract Between Planner & Executor – `AssessmentPlan`
```json
{
  "plan_id": "uuid",
  "target_topics": ["Fractions", "Basic Arithmetic"],
  "num_problems": 10,
  "difficulty_range": [1, 3],
  "reasoning_log": ["Why the plan looks this way …"]
}
```
*Rationale*: The Executor only needs concrete, machine-readable directives. The open-ended `reasoning_log` preserves chain-of-thought for observability without influencing execution.

---
## 3. Extensibility
1. **LLM integration** – Swap the body of `planner.generate_plan` for an LLM call that returns the same schema.
2. **New content types** – Extend `MathProblem` to a `BaseContent` hierarchy; executor can dispatch per type.
3. **Advanced strategies** – Add new enum values to `PedagogicalStrategy`; only the Planner needs updates.
4. **Database scaling** – Replace the JSON file with Postgres/ElasticSearch; keep the same `ProblemDatabase` interface.

---
## 4. Data & Scaling Considerations
The reference implementation lazily loads `ProblemSet.json` into memory and persists changes back to disk. This is performant for **tens of thousands** of rows (~MBs). For larger datasets simply replace the implementation with any backing store (SQL, NoSQL, vector DB). All business logic remains unchanged.

---
## 5. Running Locally

### 5.1 Manual Setup
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open http://localhost:8000/docs for an interactive Swagger UI.

### 5.2 Using Convenience Scripts
Two shell scripts are provided for quick development:

1. `run_api.sh` - Starts the API server in the background
   ```bash
   # Start server (defaults to http://127.0.0.1:8000)
   ./run_api.sh

   # Or customize host/port
   HOST=0.0.0.0 PORT=9000 ./run_api.sh
   ```
   The script will print URLs for Swagger UI, ReDoc, and where to find logs.

2. `test_request.sh` - Sends a sample assessment request
   ```bash
   # Requires jq for JSON formatting (brew install jq)
   ./test_request.sh
   ```
   This sends a POST to `/api/assessments/generate` with a pre-configured payload for quick testing.

---
## 6. Running Tests
Unit tests for the Planner and Executor live in the `tests/` package. A minimal dev setup looks like this:

```bash
# (optional) create & activate virtual-env
python -m venv venv && source venv/bin/activate

# install application deps
pip install -r requirements.txt

# install test-time dependency
pip install pytest

# run the full test-suite from the project root
pytest -q

# or, if you are already inside the hr_accuity folder
pytest tests -q
```

---
## 7. Next Steps (Beyond the Skeleton)
* ✅ Unit tests for planner/executor logic (see `tests/`).
* JWT-based auth & rate-limiting.
* Observability: OpenTelemetry traces for each orchestration stage.
* CI pipeline with pre-commit linting and type-checking.

---

