import random
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel

from models.generation import Generation
from models.duel import Duel, DuelGeneration
from models.template import Template
from models.questions import Question
from db import engine, get_db
from services.llm import generate_outputs
from services.question import set_question_winner

router = APIRouter(prefix="/questions", tags=["questions"])


class DecideDuelRequest(BaseModel):
    winner_id: int


class DuelWithGenerations(BaseModel):
    id: int
    winner_id: Optional[int]
    created_at: datetime
    decided_at: Optional[datetime]
    # Instead of question_id, we include the full question object
    question: Question
    generation_a: Generation
    generation_b: Generation


class QuestionWithSelectedGeneration(BaseModel):
    id: int
    text: str
    created_at: datetime
    selected_generation_id: Optional[int]
    selected_generation: Optional[Generation]


class QuestionResults(BaseModel):
    question: Question
    selected_generation: Optional[Generation]
    generation_performance: List[Dict[str, Any]]


def generation_and_duels_background_task(question_id: int):
    """Background task to generate outputs and save them to the database"""
    with Session(engine) as db:
        question = db.get(Question, question_id)
        if not question:
            return
        
        # Generate outputs and save them
        templates = db.exec(select(Template)).all()
        outputs = generate_outputs(templates, question)
        for output in outputs:
            db.add(output)
        db.commit()
        
        # Create duels for all generation pairs
        generations = db.exec(select(Generation).where(Generation.question_id == question_id)).all()
        for i, gen_a in enumerate(generations):
            for gen_b in generations[i+1:]:
                duel = Duel(question_id=question_id)
                db.add(duel)
                db.flush()
                db.add(DuelGeneration(duel_id=duel.id, generation_id=gen_a.id, role="generation_a"))
                db.add(DuelGeneration(duel_id=duel.id, generation_id=gen_b.id, role="generation_b"))
        db.commit()


@router.post("/", response_model=Question)
def create_question(
    question: Question, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    db.add(question)
    db.commit()
    db.refresh(question)
    
    # Add background task to generate outputs
    background_tasks.add_task(generation_and_duels_background_task, question.id)
    
    return question


@router.get("/", response_model=List[Question])
def get_questions(db: Session = Depends(get_db)):
    statement = select(Question)
    return db.exec(statement).all()


@router.get("/{question_id}", response_model=QuestionWithSelectedGeneration)
def get_question(question_id: int, db: Session = Depends(get_db)):
    # Use a LEFT JOIN to get question with its selected generation in one query
    statement = (
        select(Question, Generation)
        .outerjoin(Generation, Question.selected_generation_id == Generation.id)
        .where(Question.id == question_id)
    )
    
    result = db.exec(statement).first()
    if not result:
        raise HTTPException(status_code=404, detail="Question not found")
    
    question, selected_generation = result
    
    return QuestionWithSelectedGeneration(
        id=question.id,
        text=question.text,
        created_at=question.created_at,
        selected_generation_id=question.selected_generation_id,
        selected_generation=selected_generation
    )


@router.put("/{question_id}", response_model=Question)
def update_question(question_id: int, question: Question, db: Session = Depends(get_db)):
    db_question = db.get(Question, question_id)
    if not db_question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    for key, value in question.model_dump(exclude_unset=True).items():
        setattr(db_question, key, value)
    
    db.commit()
    db.refresh(db_question)
    return db_question


@router.delete("/{question_id}")
def delete_question(question_id: int, db: Session = Depends(get_db)):
    question = db.get(Question, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    db.delete(question)
    db.commit()
    return {"message": "Question deleted successfully"}


@router.get("/{question_id}/duels", response_model=List[Duel])
def get_duels_by_question(question_id: int, db: Session = Depends(get_db)):
    statement = select(Duel).where(Duel.question_id == question_id)
    return db.exec(statement).all()


@router.get("/{question_id}/duels/next", response_model=DuelWithGenerations)
def get_next_duel(question_id: int, db: Session = Depends(get_db)):
    """Get the next undecided duel with full question and generation data"""
    duels = db.exec(select(Duel).where(Duel.question_id == question_id, Duel.winner_id == None)).all()
    if not duels:
        raise HTTPException(status_code=404, detail="No next duel found")
    
    duel = random.choice(duels)
    
    # Get generations for this duel
    duel_gens = db.exec(select(DuelGeneration).where(DuelGeneration.duel_id == duel.id)).all()
    gen_a_id = next((dg.generation_id for dg in duel_gens if dg.role == "generation_a"), None)
    gen_b_id = next((dg.generation_id for dg in duel_gens if dg.role == "generation_b"), None)
    
    if not gen_a_id or not gen_b_id:
        raise HTTPException(status_code=404, detail="Related data not found")
    
    return DuelWithGenerations(
        id=duel.id,
        winner_id=duel.winner_id,
        created_at=duel.created_at,
        decided_at=duel.decided_at,
        question=duel.question,
        generation_a=db.get(Generation, gen_a_id),
        generation_b=db.get(Generation, gen_b_id)
    )
    


@router.post("/{question_id}/duels/{duel_id}/decide", response_model=Duel)
def decide_duel(question_id: int, duel_id: int, request: DecideDuelRequest, db: Session = Depends(get_db)):
    duel = db.get(Duel, duel_id)
    if not duel or duel.winner_id is not None:
        raise HTTPException(status_code=404 if not duel else 400, detail="Duel not found" if not duel else "Duel already decided")
    
    # Validate winner_id
    valid_ids = [dg.generation_id for dg in db.exec(select(DuelGeneration).where(DuelGeneration.duel_id == duel.id)).all() if dg.role in ["generation_a", "generation_b"]]
    if request.winner_id not in valid_ids:
        raise HTTPException(status_code=400, detail="Invalid winner ID")
    
    # Update duel
    duel.winner_id = request.winner_id
    duel.decided_at = datetime.now()
    db.commit()
    
    # Check if all duels are decided and set winner
    set_question_winner(question_id, db)
    return duel

@router.get("/{question_id}/results", response_model=QuestionResults)
def get_question_results(question_id: int, db: Session = Depends(get_db)):
    from services.performance import get_generation_performance_stats
    
    # Get the question
    question = db.get(Question, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Get the selected generation if it exists
    selected_generation = None
    if question.selected_generation_id:
        selected_generation = db.get(Generation, question.selected_generation_id)
    
    # Get generation performance stats for this question
    generation_performance = get_generation_performance_stats(question_id, db)
    
    return QuestionResults(
        question=question,
        selected_generation=selected_generation,
        generation_performance=generation_performance
    )