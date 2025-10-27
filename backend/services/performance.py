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
    # Single query with joins to get generation stats and template data
    generation_stats = db.exec(
        select(
            Generation,
            Template,
            sql_func.count(sql_func.distinct(Duel.id)).label('total_duels'),
            sql_func.sum(case((Generation.id == Duel.winner_id, 1), else_=0)).label('wins')
        )
        .select_from(Generation)
        .join(Template, Generation.template_id == Template.id)
        .outerjoin(DuelGeneration, Generation.id == DuelGeneration.generation_id)
        .outerjoin(Duel, DuelGeneration.duel_id == Duel.id)
        .where(
            Generation.question_id == question_id,
            Duel.winner_id.isnot(None)  # Only count decided duels
        )
        .group_by(Generation.id, Template.id)
    ).all()
    
    # Format the results
    performance_data = []
    for gen, template, total_duels, wins in generation_stats:
        win_rate = (wins / total_duels * 100) if total_duels > 0 else 0.0
        
        performance_data.append({
            "generation_id": gen.id,
            "template_id": gen.template_id,
            "template_name": template.name,
            "template_key": template.key,
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
    # Single query with joins to get template performance and template data
    overall_query = select(
        Template,
        sql_func.count().label('total_duels'),
        sql_func.sum(case((Generation.id == Duel.winner_id, 1), else_=0)).label('wins')
    ).select_from(
        Duel
    ).join(
        DuelGeneration, Duel.id == DuelGeneration.duel_id
    ).join(
        Generation, DuelGeneration.generation_id == Generation.id
    ).join(
        Template, Generation.template_id == Template.id
    ).join(
        Question, Duel.question_id == Question.id
    ).where(
        Duel.winner_id.isnot(None),
        Question.selected_generation_id.isnot(None)
    )
    
    # Add question filter if specified
    if question_id:
        overall_query = overall_query.where(Generation.question_id == question_id)
    
    overall_query = overall_query.group_by(Template.id)
    
    # Execute query
    overall_results = db.exec(overall_query).all()
    
    # Format overall performance
    overall_performance = []
    for template, total_duels, wins in overall_results:
        win_rate = (wins / total_duels * 100) if total_duels > 0 else 0
        overall_performance.append({
            "template_id": template.id,
            "template_name": template.name,
            "template_key": template.key,
            "wins": wins,
            "total_duels": total_duels,
            "win_rate": round(win_rate, 2)
        })
    
    # Sort overall by win rate descending
    overall_performance.sort(key=lambda x: x["win_rate"], reverse=True)
    
    return {
        "overall": overall_performance
    }
