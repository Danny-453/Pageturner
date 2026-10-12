from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models import Question, QuestionOption, Topic, User
from app.schemas.question import AnswerRequest, AnswerResult, QuestionAdminOut, QuestionCreate, QuestionOut, QuestionUpdate
from app.services.answer_service import submit_answer
from app.services.learning_service import current_learning_level

router = APIRouter(prefix="/questions", tags=["Questions"])


def public_question(q: Question) -> QuestionOut:
    return QuestionOut.model_validate(q)

@router.get("", response_model=list[QuestionOut])
def list_questions(course_id: str | None = None, topic_id: str | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    stmt = select(Question).options(selectinload(Question.options)).join(Topic).where(Question.is_published.is_(True))
    if course_id: stmt = stmt.where(Topic.course_id == course_id)
    if topic_id: stmt = stmt.where(Question.topic_id == topic_id)
    return [public_question(q) for q in db.scalars(stmt).all()]

@router.get("/{question_id}", response_model=QuestionOut)
def get_question(question_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = db.scalar(select(Question).options(selectinload(Question.options)).where(Question.id == question_id, Question.is_published.is_(True)))
    if not q: raise HTTPException(status_code=404, detail="Question not found.")
    return public_question(q)

@router.get("/{question_id}/admin", response_model=QuestionAdminOut, dependencies=[Depends(require_admin)])
def get_question_for_admin(question_id: str, db: Session = Depends(get_db)):
    q = db.scalar(select(Question).options(selectinload(Question.options)).where(Question.id == question_id))
    if not q: raise HTTPException(status_code=404, detail="Question not found.")
    return q

@router.post("/{question_id}/answer", response_model=AnswerResult)
def answer_question(question_id: str, payload: AnswerRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = db.scalar(select(Question).where(Question.id == question_id, Question.is_published.is_(True)))
    if not q: raise HTTPException(status_code=404, detail="Question not found.")
    option_keys = {o.option_key for o in db.scalars(select(QuestionOption).where(QuestionOption.question_id == q.id)).all()}
    if option_keys and payload.answer_id not in option_keys:
        raise HTTPException(status_code=400, detail="Selected answer is not a valid option.")
    _, level = submit_answer(db, user, q, payload.answer_id)
    return AnswerResult(
        correct=payload.answer_id == q.correct_answer, points=q.points if payload.answer_id == q.correct_answer else 0,
        explanation=q.explanation, total_points=user.total_points, questions_answered=user.questions_answered,
        correct_answers=user.correct_answers, learning_level=level.level if level else 1,
    )

@router.post("", response_model=QuestionOut, status_code=201, dependencies=[Depends(require_admin)])
def create_question(payload: QuestionCreate, db: Session = Depends(get_db)):
    if not db.get(Topic, payload.topic_id): raise HTTPException(status_code=400, detail="Topic does not exist.")
    data = payload.model_dump(exclude={"options"})
    q = Question(**data); db.add(q); db.flush()
    for option in payload.options: db.add(QuestionOption(question_id=q.id, **option.model_dump()))
    db.commit()
    q = db.scalar(select(Question).options(selectinload(Question.options)).where(Question.id == q.id))
    return public_question(q)

@router.patch("/{question_id}", response_model=QuestionOut, dependencies=[Depends(require_admin)])
def update_question(question_id: str, payload: QuestionUpdate, db: Session = Depends(get_db)):
    q = db.get(Question, question_id)
    if not q: raise HTTPException(status_code=404, detail="Question not found.")
    data = payload.model_dump(exclude_unset=True, exclude={"options"})
    for key, value in data.items(): setattr(q, key, value)
    if payload.options is not None:
        for option in list(q.options): db.delete(option)
        db.flush()
        for option in payload.options: db.add(QuestionOption(question_id=q.id, **option.model_dump()))
    db.commit()
    q = db.scalar(select(Question).options(selectinload(Question.options)).where(Question.id == q.id))
    return public_question(q)

@router.delete("/{question_id}", status_code=204, dependencies=[Depends(require_admin)])
def delete_question(question_id: str, db: Session = Depends(get_db)):
    q = db.get(Question, question_id)
    if not q: raise HTTPException(status_code=404, detail="Question not found.")
    db.delete(q); db.commit()
