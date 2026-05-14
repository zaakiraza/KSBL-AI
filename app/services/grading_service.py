from __future__ import annotations

import re
from collections import Counter

from app.models.schemas import Feedback, QuestionResult, ResultResponse, SectionBreakdown

STOPWORDS = {
    "the",
    "and",
    "of",
    "to",
    "a",
    "in",
    "is",
    "it",
    "that",
    "for",
    "on",
    "with",
    "as",
    "this",
    "by",
}


def _normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def _extract_keywords(text: str) -> set[str]:
    words = [word for word in _normalize(text).split() if word not in STOPWORDS and len(word) > 2]
    return set(words)


def _score_short_answer(response_text: str, reference_answer: str) -> tuple[float, bool]:
    response_keywords = _extract_keywords(response_text)
    reference_keywords = _extract_keywords(reference_answer)
    if not response_keywords or not reference_keywords:
        return 0.0, False
    overlap = response_keywords.intersection(reference_keywords)
    ratio = len(overlap) / max(1, len(reference_keywords))
    score = 1.0 if ratio >= 0.75 else 0.5 if ratio >= 0.35 else 0.0
    return score, score > 0.0


def grade_attempt(quiz: dict, attempt: dict) -> ResultResponse:
    responses = {response["questionId"]: response for response in attempt["responses"]}
    question_results: list[QuestionResult] = []
    total_score = 0.0
    max_score = float(len(quiz["questions"]))
    topic_scores: Counter[str] = Counter()
    topic_totals: Counter[str] = Counter()

    for question in quiz["questions"]:
        response = responses.get(question["questionId"], {})
        q_type = question["type"]
        correct = False
        score = 0.0
        chosen_answer = None
        reference_answer = None

        if q_type == "mcq":
            chosen_answer = response.get("choiceId")
            correct = chosen_answer == question.get("correctOptionId")
            score = 1.0 if correct else 0.0
            reference_answer = question.get("correctOptionId")
        elif q_type == "true_false":
            chosen_answer = str(response.get("trueFalse"))
            correct = response.get("trueFalse") == question.get("trueFalseCorrect")
            score = 1.0 if correct else 0.0
            reference_answer = str(question.get("trueFalseCorrect"))
        elif q_type == "fitb":
            answer_text = " ".join(response.get("blankAnswers", []))
            chosen_answer = answer_text
            accepted_variants = []
            for blank in question.get("blanks", []):
                accepted_variants.extend(blank.get("correctAnswers", []))
                accepted_variants.extend(blank.get("variants", []))
            normalized_answer = _normalize(answer_text)
            correct = any(normalized_answer == _normalize(candidate) for candidate in accepted_variants)
            score = 1.0 if correct else 0.0
            reference_answer = accepted_variants[0] if accepted_variants else ""
        else:
            response_text = response.get("shortAnswerText") or ""
            chosen_answer = response_text
            reference_answer = question.get("shortAnswerReferenceAnswers", [""])[0]
            score, correct = _score_short_answer(response_text, reference_answer)

        total_score += score
        topic = question.get("topic", "General")
        topic_scores[topic] += score
        topic_totals[topic] += 1
        question_results.append(
            QuestionResult(
                questionId=question["questionId"],
                type=q_type,
                correct=correct,
                score=score,
                maxScore=1.0,
                chosenAnswer=chosen_answer,
                referenceAnswer=reference_answer,
                rationale=question.get("rationale"),
                evidenceSources=question.get("citations", []),
            )
        )

    missed_topics = [topic for topic, total in topic_totals.items() if topic_scores[topic] < total]
    strengths = [topic for topic, total in topic_totals.items() if topic_scores[topic] == total]
    weaknesses = missed_topics[:3]
    study_suggestions = [f"Review the section related to {topic}." for topic in weaknesses] or ["Revise the chapter notes and retry the quiz."]

    return ResultResponse(
        studentId=attempt["studentId"],
        classId=attempt["classId"],
        teacherId=attempt["teacherId"],
        quizId=attempt["quizId"],
        attemptId=attempt["attemptId"],
        totalScore=total_score,
        maxScore=max_score,
        sectionBreakdown=[
            SectionBreakdown(sectionId=topic, score=float(score), maxScore=float(total))
            for topic, score in topic_scores.items()
            for topic2, total in [(topic, topic_totals[topic])]
        ],
        questions=question_results,
        feedback=Feedback(
            summary=f"Scored {total_score:.1f} out of {max_score:.1f}.",
            strengths=strengths,
            weaknesses=weaknesses,
            studySuggestions=study_suggestions,
        ),
        metadata={
            "startedAt": str(attempt["startedAt"]),
            "submittedAt": str(attempt["submittedAt"]),
            "durationSec": str(int((attempt["submittedAt"] - attempt["startedAt"]).total_seconds())),
            "flags": "[]",
            "version": "1",
        },
    )
