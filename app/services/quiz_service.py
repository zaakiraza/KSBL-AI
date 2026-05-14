from __future__ import annotations

from collections import Counter
from itertools import cycle
from typing import Iterable

from app.models.schemas import (
    Citation,
    FitbBlank,
    GenerationPreferences,
    ApproveQuizResponse,
    QuizDraftResponse,
    QuizOption,
    QuizQuestion,
    ReviewArtifact,
)
from app.services.state import QUIZZES, new_id, now_utc


DIFFICULTY_SEQUENCE = ["easy", "medium", "medium", "hard"]


def _topic_from_chunk(chunk_text: str, index: int) -> str:
    words = [word for word in chunk_text.split() if len(word) > 4]
    if not words:
        return f"Topic {index + 1}"
    return " ".join(words[:2]).title()


def _pick_source_chunks(chunks: list[dict], count: int) -> list[dict]:
    if not chunks:
        return [{"chunkId": new_id("chunk"), "text": "No content provided.", "sectionPath": "Unknown"}]
    selected = []
    for index in range(count):
        selected.append(chunks[index % len(chunks)])
    return selected


def _make_question(chunk: dict, question_type: str, index: int) -> QuizQuestion:
    text = chunk["text"]
    topic = _topic_from_chunk(text, index)
    difficulty = DIFFICULTY_SEQUENCE[index % len(DIFFICULTY_SEQUENCE)]
    stem = f"According to the provided material, what is the key idea in the following excerpt? {text[:180]}"
    citations = [
        Citation(docId=chunk.get("chunkId", "unknown"), page=chunk.get("pageStart"), span=text[:200])
    ]

    if question_type == "mcq":
        keywords = [word.strip(".,") for word in text.split() if len(word) > 4][:4]
        if len(keywords) < 4:
            keywords = keywords + [f"Option {position + 1}" for position in range(4 - len(keywords))]
        options = [QuizOption(optionId=f"opt_{index}_{position}", text=keyword) for position, keyword in enumerate(keywords[:4])]
        return QuizQuestion(
            questionId=new_id("question"),
            type="mcq",
            stem=stem,
            topic=topic,
            difficulty=difficulty,
            options=options,
            correctOptionId=options[0].optionId,
            rationale="The correct option is derived from the most relevant keyword in the source excerpt.",
            citations=citations,
        )

    if question_type == "true_false":
        return QuizQuestion(
            questionId=new_id("question"),
            type="true_false",
            stem=f"True or False: {topic} is supported by the source material.",
            topic=topic,
            difficulty=difficulty,
            trueFalseCorrect=(index % 2 == 0),
            rationale="This statement is directly grounded in the source excerpt.",
            citations=citations,
        )

    if question_type == "fitb":
        answer = text.split()[0] if text.split() else "content"
        blank = FitbBlank(blankId=f"blank_{index}", correctAnswers=[answer], variants=[answer.lower(), answer.upper()])
        return QuizQuestion(
            questionId=new_id("question"),
            type="fitb",
            stem=f"Fill in the blank: {answer} is an important concept in the lesson.",
            topic=topic,
            difficulty=difficulty,
            blanks=[blank],
            rationale="The blank is anchored to a key term from the source.",
            citations=citations,
        )

    reference = text[:120] if text else "Summarize the source excerpt."
    rubric = [
        {"criterionId": f"crit_{index}_1", "description": "Identifies the main idea", "points": 1},
        {"criterionId": f"crit_{index}_2", "description": "Uses the source accurately", "points": 1},
    ]
    return QuizQuestion(
        questionId=new_id("question"),
        type="short_answer",
        stem=f"Explain the main idea of: {text[:160]}",
        topic=topic,
        difficulty=difficulty,
        shortAnswerReferenceAnswers=[reference],
        shortAnswerRubric=[
            {"criterionId": item["criterionId"], "description": item["description"], "points": item["points"]}
            for item in rubric
        ],
        rationale="The answer should demonstrate understanding of the excerpt.",
        citations=citations,
    )


def _build_questions(chunks: list[dict], preferences: GenerationPreferences) -> list[QuizQuestion]:
    selected_chunks = _pick_source_chunks(chunks, preferences.count)
    question_types = preferences.questionTypes or ["mcq", "true_false", "fitb", "short_answer"]
    type_cycle = cycle(question_types)
    questions = []
    for index, chunk in enumerate(selected_chunks):
        questions.append(_make_question(chunk, next(type_cycle), index))
    return questions


def _confidence_report(questions: Iterable[QuizQuestion]) -> dict[str, float | list[str]]:
    question_list = list(questions)
    flags = [question.questionId for question in question_list if len(question.citations) == 0]
    confidence = 0.9 if not flags else 0.6
    return {"avg": confidence, "min": confidence, "flags": flags}


def generate_quiz_bundle(ingestion_record: dict, preferences: GenerationPreferences) -> tuple[QuizDraftResponse, ReviewArtifact]:
    questions = _build_questions(ingestion_record["chunks"], preferences)
    quiz_id = new_id("quiz")
    version = 1
    title = ingestion_record["title"]
    draft = QuizDraftResponse(
        quizId=quiz_id,
        title=title,
        version=version,
        timeLimitSec=preferences.timeLimitMin * 60,
        questions=questions,
        confidence=_confidence_report(questions),
    )
    review_artifact = ReviewArtifact(
        quizId=quiz_id,
        version=version,
        editableFields=[
            "stem",
            "options",
            "correctOptionId",
            "trueFalseCorrect",
            "blanks",
            "shortAnswerReferenceAnswers",
            "shortAnswerRubric",
            "rationale",
            "difficulty",
            "topic",
        ],
        questions=questions,
    )
    QUIZZES[quiz_id] = {
        "quizId": quiz_id,
        "title": title,
        "version": version,
        "status": "draft",
        "timeLimitSec": preferences.timeLimitMin * 60,
        "questions": [question.model_dump() for question in questions],
        "reviewArtifact": review_artifact.model_dump(),
        "createdAt": now_utc(),
        "ingestionId": ingestion_record["ingestionId"],
    }
    return draft, review_artifact


def approve_quiz(quiz_id: str, version: int, approver_id: str) -> ApproveQuizResponse:
    quiz = QUIZZES[quiz_id]
    quiz["status"] = "approved"
    quiz["approvedBy"] = approver_id
    quiz["approvedAt"] = now_utc()
    etag = f"{quiz_id}:{version}:{approver_id}"
    return ApproveQuizResponse(quizId=quiz_id, version=version, signedAt=now_utc(), etag=etag)
