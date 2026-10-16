from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.api.deps import require_admin
from app.db.session import get_db
from app.models import Course, Lesson, Question, QuestionOption, StudentProgress, User
from app.schemas.quiz_generation import GeneratedQuiz
from app.services.quiz_generation_service import (
    QuizGenerationNotConfiguredError,
    QuizGenerationUnavailableError,
    generate_lesson_quiz,
)

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/analytics", dependencies=[Depends(require_admin)])
def analytics(db: Session = Depends(get_db)):
    return {
        "students": db.scalar(select(func.count(User.id)).where(User.role == "student")) or 0,
        "courses": db.scalar(select(func.count(Course.id))) or 0,
        "questions": db.scalar(select(func.count(Question.id))) or 0,
        "progress_records": db.scalar(select(func.count(StudentProgress.id))) or 0,
    }


def _lesson_for_quiz_generation(lesson_id: str, db: Session) -> Lesson:
    lesson = db.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found.")
    existing_count = db.scalar(
        select(func.count(Question.id)).where(Question.source_lesson_id == lesson.id)
    ) or 0
    if existing_count:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This lesson already has AI-generated questions. Delete them before generating a new set.",
        )
    if not lesson.content.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Add lesson content before generating questions.",
        )
    return lesson


@router.post(
    "/lessons/{lesson_id}/generate-questions",
    response_model=GeneratedQuiz,
    dependencies=[Depends(require_admin)],
)
def generate_questions_for_lesson(lesson_id: str, db: Session = Depends(get_db)):
    lesson = _lesson_for_quiz_generation(lesson_id, db)
    try:
        return generate_lesson_quiz(lesson.title, lesson.content)
    except QuizGenerationNotConfiguredError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except QuizGenerationUnavailableError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.post(
    "/lessons/{lesson_id}/questions",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def save_generated_questions_for_lesson(
    lesson_id: str,
    payload: GeneratedQuiz,
    db: Session = Depends(get_db),
):
    lesson = _lesson_for_quiz_generation(lesson_id, db)
    for generated in payload.questions:
        question = Question(
            topic_id=lesson.topic_id,
            source_lesson_id=lesson.id,
            question_text=generated.question_text,
            difficulty=generated.difficulty,
            explanation=generated.explanation,
            points=10,
            correct_answer=generated.correct_answer,
            is_published=True,
        )
        db.add(question)
        db.flush()
        for order, option in enumerate(generated.options, start=1):
            db.add(
                QuestionOption(
                    question_id=question.id,
                    option_key=option.option_key,
                    text=option.text,
                    order=order,
                )
            )
    db.commit()
    return {"lesson_id": lesson.id, "saved_count": len(payload.questions)}
