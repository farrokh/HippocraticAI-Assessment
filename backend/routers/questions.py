import random
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlmodel import Session, select

from models.generation import Generation
from models.duel import Duel, DuelGeneration, DuelWithGenerations, DecideDuelRequest
from models.template import Template
from models.questions import Question, QuestionWithSelectedGeneration, QuestionResults
from db import engine, get_db
from services.llm import generate_outputs
from services.question import set_question_winner

router = APIRouter(prefix="/questions", tags=["questions"])


def generation_and_duels_background_task(question_id: int):
    """Background task to generate outputs and save them to the database"""
    with Session(engine) as db:
        question = db.exec(select(Question).where(Question.id == question_id)).first()
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


def _build_question_with_generation(question: Question, selected_generation: Optional[Generation] = None) -> QuestionWithSelectedGeneration:
    """Helper function to build QuestionWithSelectedGeneration from question and optional generation"""
    return QuestionWithSelectedGeneration(
        id=question.id,
        text=question.text,
        created_at=question.created_at,
        selected_generation_id=question.selected_generation_id,
        selected_generation=selected_generation
    )


@router.get("/", response_model=List[QuestionWithSelectedGeneration])
def get_questions(limit: int = 10, details: bool = False, db: Session = Depends(get_db)):
    """Get list of questions with optional selected generation details"""
    if details:
        # When details=True, use LEFT JOIN to fetch generations in one query
        statement = (
            select(Question, Generation)
            .outerjoin(Generation, Question.selected_generation_id == Generation.id)
            .order_by(Question.created_at.desc())
            .limit(limit)
        )
        results = db.exec(statement).all()
        return [
            _build_question_with_generation(question, selected_generation)
            for question, selected_generation in results
        ]
    else:
        # When details=False, only fetch questions (more efficient)
        statement = (
            select(Question)
            .order_by(Question.created_at.desc())
            .limit(limit)
        )
        results = db.exec(statement).all()
        return [
            _build_question_with_generation(question, None)
            for question in results
        ]


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
    return _build_question_with_generation(question, selected_generation)


@router.put("/{question_id}", response_model=Question)
def update_question(question_id: int, question: Question, db: Session = Depends(get_db)):
    db_question = db.exec(select(Question).where(Question.id == question_id)).first()
    if not db_question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    for key, value in question.model_dump(exclude_unset=True).items():
        setattr(db_question, key, value)
    
    db.commit()
    db.refresh(db_question)
    return db_question


@router.delete("/{question_id}")
def delete_question(question_id: int, db: Session = Depends(get_db)):
    question = db.exec(select(Question).where(Question.id == question_id)).first()
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
    """Get the next undecided duel with full question and generation data
    
    Returns:
        - 404: Question not found
        - 202: Question is still being processed (generations or duels not ready)
        - 204: All duels have been decided (no more comparisons available)
        - 200: Returns the next duel
    """
    # First, verify the question exists
    question = db.exec(select(Question).where(Question.id == question_id)).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Check if generations exist for this question
    generations = db.exec(select(Generation).where(Generation.question_id == question_id)).all()
    if not generations:
        # Question exists but generations haven't been created yet - still processing
        raise HTTPException(status_code=202, detail="Question is still being processed")
    
    # Check if duels exist for this question
    duels = db.exec(select(Duel).where(Duel.question_id == question_id)).all()
    if not duels:
        # Generations exist but duels haven't been created yet - still processing
        raise HTTPException(status_code=202, detail="Duels are still being created")
    
    # Single query with joins to get everything at once, including the role
    statement = (
        select(Duel, Generation, Question, DuelGeneration.role)
        .join(DuelGeneration, Duel.id == DuelGeneration.duel_id)
        .join(Generation, DuelGeneration.generation_id == Generation.id)
        .join(Question, Duel.question_id == Question.id)
        .where(Duel.question_id == question_id, Duel.winner_id == None)
    )
    
    results = db.exec(statement).all()
    if not results:
        # Question exists, generations exist, duels exist, but all are decided
        # This is not an error - it's a completion state
        raise HTTPException(status_code=204, detail="All duels have been decided")
    
    # Group results by duel_id to handle the two generations per duel
    duels_data = {}
    for duel, generation, question, role in results:
        if duel.id not in duels_data:
            duels_data[duel.id] = {
                'duel': duel,
                'question': question,
                'generations': {}
            }
        
        duels_data[duel.id]['generations'][role] = generation
    
    # Pick a random duel that has both generations
    valid_duels = [data for data in duels_data.values() 
                   if 'generation_a' in data['generations'] and 'generation_b' in data['generations']]
    
    if not valid_duels:
        # Duels exist but none are complete - still processing
        raise HTTPException(status_code=202, detail="Duels are still being created")
    
    duel_data = random.choice(valid_duels)
    duel = duel_data['duel']
    
    return DuelWithGenerations(
        id=duel.id,
        winner_id=duel.winner_id,
        created_at=duel.created_at,
        decided_at=duel.decided_at,
        question=duel_data['question'],
        generation_a=duel_data['generations']['generation_a'],
        generation_b=duel_data['generations']['generation_b']
    )
    


@router.post("/{question_id}/duels/{duel_id}/decide", response_model=Duel)
def decide_duel(question_id: int, duel_id: int, request: DecideDuelRequest, db: Session = Depends(get_db)):
    # Single query to get duel and validate winner_id in one go
    statement = (
        select(Duel, DuelGeneration.generation_id)
        .join(DuelGeneration, Duel.id == DuelGeneration.duel_id)
        .where(
            Duel.id == duel_id,
            DuelGeneration.role.in_(["generation_a", "generation_b"])
        )
    )
    
    results = db.exec(statement).all()
    if not results:
        raise HTTPException(status_code=404, detail="Duel not found")
    
    duel = results[0][0]  # All results have the same duel
    valid_generation_ids = [result[1] for result in results]
    
    if duel.winner_id is not None:
        raise HTTPException(status_code=400, detail="Duel already decided")
    
    if request.winner_id not in valid_generation_ids:
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
    
    # Single query to get question with its selected generation
    statement = (
        select(Question, Generation)
        .outerjoin(Generation, Question.selected_generation_id == Generation.id)
        .where(Question.id == question_id)
    )
    
    result = db.exec(statement).first()
    if not result:
        raise HTTPException(status_code=404, detail="Question not found")
    
    question, selected_generation = result
    
    # Get generation performance stats for this question
    generation_performance = get_generation_performance_stats(question_id, db)
    
    return QuestionResults(
        question=question,
        selected_generation=selected_generation,
        generation_performance=generation_performance
    )