from sqlmodel import Session, select
from models.duel import Duel, DuelGeneration
from models.generation import Generation
from models.template import Template
from models.questions import Question
from collections import Counter
from db import engine

def generation_and_duels_background_task(question_id: int):
    """Background task to generate outputs and save them to the database"""
    from services.llm import generate_outputs
    
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


def set_question_winner(question_id: int, db: Session):
    """
    Set the selected_generation_id for a question when all duels are completed.
    
    Uses a simple vote-counting system: the generation that wins the most duels
    becomes the selected generation. In case of ties, the generation with the 
    lowest ID is selected (deterministic tie-breaking).
    """
    # Check if all duels are decided
    undecided = db.exec(select(Duel).where(Duel.question_id == question_id, Duel.winner_id == None)).first()
    if undecided:
        return None
    
    # Get all winners for this question
    # Since we've already checked that all duels are decided, we can query all duels
    # without the winner_id != None filter, but keeping it for extra safety
    all_duels = db.exec(select(Duel).where(Duel.question_id == question_id, Duel.winner_id != None)).all()
    if not all_duels:
        return None
    
    # Count wins for each generation
    winners = [duel.winner_id for duel in all_duels]
    winner_counts = Counter(winners)
    
    if not winner_counts:
        return None
    
    # Find the generation with the most wins
    max_wins = winner_counts.most_common(1)[0][1]
    top_winners = [gen_id for gen_id, count in winner_counts.items() if count == max_wins]
    
    # Handle ties: use the generation with the lowest ID (deterministic)
    winner_id = min(top_winners)
    
    # Update the question
    question = db.get(Question, question_id)
    if not question:
        return None
    
    question.selected_generation_id = winner_id
    db.commit()
    return question