#!/usr/bin/env bash
# test_request.sh – send one POST to /api/assessments/generate

HOST=${HOST:-127.0.0.1}
PORT=${PORT:-8000}
URL="http://${HOST}:${PORT}/api/assessments/generate"

# Sample payload
read -r -d '' PAYLOAD << 'EOF'
{
  "student_profile": {
    "id": "test-student",
    "mastered_topics": ["Basic Arithmetic"],
    "learning_goals": ["Introduction to Algebra"]
  },
  "assessment_request": {
    "max_total_time_minutes": 10,
    "pedagogical_strategy": "REVIEW"
  }
}
EOF

echo "→ Sending POST to $URL"
curl -s -X POST "$URL" \
     -H "Content-Type: application/json" \
     -d "$PAYLOAD" \
| jq .
