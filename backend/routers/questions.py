import datetime
import random
from typing import List
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel

from models.generation import Generation
from models.duel import Duel
from models.template import Template
from models.questions import Question
from db import engine, get_db
from services.llm import generate_outputs

router = APIRouter(prefix="/questions", tags=["questions"])


class DecideDuelRequest(BaseModel):
    winner_id: int


def generation_and_duels_background_task(question_id: int):
    """Background task to generate outputs and save them to the database"""
    with Session(engine) as db:
        from sqlmodel import select
        question = db.get(Question, question_id)
        if not question:
            return
        
        # Get all templates
        templates = db.exec(select(Template)).all()
        
        # Generate outputs using the templates
        outputs = generate_outputs(templates, question)
        
        # Save generations to database
        for output in outputs:
            db.add(output)
        
        db.commit()
        
        # Generate duels between all pairs of generations
        generations = db.exec(select(Generation).where(Generation.question_id == question_id)).all()
        
        # Create duels for all unique pairs (avoid duplicates like A vs B and B vs A)
        for i, generation_a in enumerate(generations):
            for generation_b in generations[i+1:]:
                db.add(Duel(
                    question_id=question_id,
                    generation_a_id=generation_a.id,
                    generation_b_id=generation_b.id
                ))
        
        db.commit()
        print(f"✓ Generated {len(outputs)} outputs and {len(generations) * (len(generations) - 1) // 2} duels for question {question_id}")


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


@router.get("/{question_id}", response_model=Question)
def get_question(question_id: int, db: Session = Depends(get_db)):
    question = db.get(Question, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@router.put("/{question_id}", response_model=Question)
def update_question(question_id: int, question: Question, db: Session = Depends(get_db)):
    db_question = db.get(Question, question_id)
    if not db_question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    for key, value in question.model_dump(exclude_unset=True).items():
        setattr(db_question, key, value)
    
    db.add(db_question)
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


@router.get("/{question_id}/duels/next", response_model=Duel)
def get_next_duel(question_id: int, db: Session = Depends(get_db)):
    statement = select(Duel).where(Duel.question_id == question_id).where(Duel.winner_id == None).order_by(Duel.created_at.asc())
    duels = db.exec(statement)
    if not duels:
        raise HTTPException(status_code=404, detail="No next duel found")
    # return random duel from the list
    return random.choice(duels.all())


@router.post("/{question_id}/duels/{duel_id}/decide", response_model=Duel)
def decide_duel(
    question_id: int,
    duel_id: int, 
    request: DecideDuelRequest,
    db: Session = Depends(get_db)
):
    duel = db.get(Duel, duel_id)
    if not duel:
        raise HTTPException(status_code=404, detail="Duel not found")
    
    if duel.winner_id is not None:
        raise HTTPException(status_code=400, detail="Duel already decided")
    
    # Validate that winner_id is one of the two generations in the duel
    valid_ids = [duel.generation_a_id, duel.generation_b_id]
    if request.winner_id not in valid_ids:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid winner ID. Must be either {duel.generation_a_id} or {duel.generation_b_id}"
        )
    
    # Set the winner
    duel.winner_id = request.winner_id
    duel.decided_at = datetime.datetime.now()
    
    db.add(duel)
    db.commit()
    db.refresh(duel)
    return duel