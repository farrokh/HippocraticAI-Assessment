from sqlmodel import Session, select
from models.duel import Duel
from models.questions import Question
from collections import Counter

def set_question_winner(question_id: int, db: Session):
    """Set the selected_generation_id for a question when all duels are completed"""
    # Check if all duels are decided
    undecided = db.exec(select(Duel).where(Duel.question_id == question_id, Duel.winner_id == None)).first()
    if undecided:
        return None
    
    # Get all winners and find the most frequent one
    winners = [duel.winner_id for duel in db.exec(select(Duel).where(Duel.question_id == question_id, Duel.winner_id != None)).all()]
    if not winners:
        return None
    
    winner_id = Counter(winners).most_common(1)[0][0]
    
    # Update the question
    question = db.get(Question, question_id)
    question.selected_generation_id = winner_id
    db.commit()
    return question