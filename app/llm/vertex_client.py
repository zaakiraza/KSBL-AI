from __future__ import annotations

from app.models.schemas import QuizQuestion, RubricCriterion


class VertexLLMClient:
    def generate_question(self, prompt: str) -> QuizQuestion:
        return QuizQuestion(
            questionId="mock-question",
            type="short_answer",
            stem=prompt[:120],
            topic="Mock Topic",
            difficulty="medium",
            shortAnswerReferenceAnswers=[prompt[:120]],
            shortAnswerRubric=[RubricCriterion(criterionId="crit_1", description="Matches prompt", points=1)],
        )
