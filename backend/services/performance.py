from typing import List, Dict, Any, Optional
from sqlmodel import Session, select, case, func as sql_func
from models.duel import Duel, DuelGeneration
from models.generation import Generation
from models.questions import Question
from models.template import Template


def get_generation_performance_stats(question_id: int, db: Session) -> List[Dict[str, Any]]:
    """
    Get performance statistics for all generations of a specific question.
    Returns list of generation performance data with win rates.
    """
    # Query to get generation stats for a specific question
    # Count unique duels per generation, not all DuelGeneration entries
    generation_stats = db.exec(
        select(
            Generation,
            sql_func.count(sql_func.distinct(Duel.id)).label('total_duels'),
            sql_func.sum(case((Generation.id == Duel.winner_id, 1), else_=0)).label('wins')
        )
        .select_from(Generation)
        .outerjoin(DuelGeneration, Generation.id == DuelGeneration.generation_id)
        .outerjoin(Duel, DuelGeneration.duel_id == Duel.id)
        .where(
            Generation.question_id == question_id,
            Duel.winner_id.isnot(None)  # Only count decided duels
        )
        .group_by(Generation.id)
    ).all()
    
    # Get template data for context
    all_templates = {t.id: t for t in db.exec(select(Template)).all()}
    
    # Format the results
    performance_data = []
    for gen, total_duels, wins in generation_stats:
        template = all_templates.get(gen.template_id)
        win_rate = (wins / total_duels * 100) if total_duels > 0 else 0.0
        
        performance_data.append({
            "generation_id": gen.id,
            "template_id": gen.template_id,
            "template_name": template.name if template else f"Template {gen.template_id}",
            "template_key": template.key if template else None,
            "output_text": gen.output_text,
            "llm_model": gen.llm_model,
            "latency": gen.latency,
            "output_tokens": gen.output_tokens,
            "input_tokens": gen.input_tokens,
            "created_at": gen.created_at,
            "wins": wins or 0,
            "total_duels": total_duels or 0,
            "win_rate": round(win_rate, 2)
        })
    
    # Sort by win rate descending
    performance_data.sort(key=lambda x: x["win_rate"], reverse=True)
    
    return performance_data


def get_template_performance_stats(db: Session, question_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Get template performance statistics, optionally filtered by question.
    Reuses the logic from templates.py but allows filtering by question.
    """
    # Base query for overall performance
    overall_query = select(
        Generation.template_id,
        sql_func.count().label('total_duels'),
        sql_func.sum(case((Generation.id == Duel.winner_id, 1), else_=0)).label('wins')
    ).select_from(
        Duel
    ).join(
        DuelGeneration, Duel.id == DuelGeneration.duel_id
    ).join(
        Generation, DuelGeneration.generation_id == Generation.id
    ).join(
        Question, Duel.question_id == Question.id
    ).where(
        Duel.winner_id.isnot(None),
        Question.selected_generation_id.isnot(None)
    )
    
    # Add question filter if specified
    if question_id:
        overall_query = overall_query.where(Generation.question_id == question_id)
    
    overall_query = overall_query.group_by(Generation.template_id)
    
    # Execute query
    overall_results = db.exec(overall_query).all()
    
    # Get all templates
    all_templates = {t.id: t for t in db.exec(select(Template)).all()}
    
    # Format overall performance
    overall_performance = []
    for row in overall_results:
        template = all_templates.get(row.template_id)
        win_rate = (row.wins / row.total_duels * 100) if row.total_duels > 0 else 0
        overall_performance.append({
            "template_id": row.template_id,
            "template_name": template.name if template else f"Template {row.template_id}",
            "template_key": template.key if template else None,
            "wins": row.wins,
            "total_duels": row.total_duels,
            "win_rate": round(win_rate, 2)
        })
    
    # Sort overall by win rate descending
    overall_performance.sort(key=lambda x: x["win_rate"], reverse=True)
    
    return {
        "overall": overall_performance
    }
