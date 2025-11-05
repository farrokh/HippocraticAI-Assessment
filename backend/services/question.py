from sqlmodel import Session, select
from models.duel import Duel
from models.questions import Question
from collections import Counter

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