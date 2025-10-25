from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, case

from models.template import Template
from models.duel import Duel, DuelGeneration
from models.generation import Generation
from models.questions import Question
from db import get_db

router = APIRouter(prefix="/templates", tags=["templates"])


@router.post("/", response_model=Template)
def create_template(template: Template, db: Session = Depends(get_db)):
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.get("/", response_model=List[Template])
def get_templates(db: Session = Depends(get_db)):
    statement = select(Template)
    return db.exec(statement).all()


@router.get("/performance", response_model=Dict[str, Any])
def get_template_performance(
    overall_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get template performance based on duel results.
    Returns win rates grouped by question and overall win rate.
    Optimized with SQL joins and aggregations.
    
    Args:
        overall_only: If True, return only overall performance. If False, return both overall and by-question.
    """
    from services.performance import get_template_performance_stats
    
    # Get overall performance using shared service
    overall_performance = get_template_performance_stats(db)["overall"]
    
    # If overall_only flag is set, return early with just overall performance
    if overall_only:
        return {
            "overall": overall_performance
        }
    
    # For by_question data, we need to implement the per-question logic
    # This is more complex and specific to the templates endpoint
    from sqlmodel import func as sql_func
    
    # Single optimized query for per-question performance
    question_query = select(
        Generation.template_id,
        Duel.question_id,
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
    ).group_by(
        Generation.template_id,
        Duel.question_id
    )
    
    # Execute question query
    question_results = db.exec(question_query).all()
    
    # Get all templates and questions
    all_templates = {t.id: t for t in db.exec(select(Template)).all()}
    all_questions = {q.id: q for q in db.exec(select(Question)).all()}
    
    # Format per-question performance
    question_performance_map: Dict[int, List[Dict[str, Any]]] = {}
    
    for row in question_results:
        question_id = row.question_id
        if question_id not in question_performance_map:
            question = all_questions.get(question_id)
            question_performance_map[question_id] = {
                "question_data": {
                    "question_id": question_id,
                    "question_text": question.text if question else f"Question {question_id}",
                    "template_performance": []
                }
            }
        
        template = all_templates.get(row.template_id)
        win_rate = (row.wins / row.total_duels * 100) if row.total_duels > 0 else 0
        
        question_performance_map[question_id]["question_data"]["template_performance"].append({
            "template_id": row.template_id,
            "template_name": template.name if template else f"Template {row.template_id}",
            "template_key": template.key if template else None,
            "wins": row.wins,
            "total_duels": row.total_duels,
            "win_rate": round(win_rate, 2)
        })
    
    # Sort each question's templates by win rate and format final structure
    by_question = []
    for question_id, data in question_performance_map.items():
        data["question_data"]["template_performance"].sort(key=lambda x: x["win_rate"], reverse=True)
        by_question.append(data["question_data"])
    
    return {
        "by_question": by_question,
        "overall": overall_performance
    }


@router.get("/{template_id}", response_model=Template)
def get_template(template_id: int, db: Session = Depends(get_db)):
    template = db.get(Template, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.put("/{template_id}", response_model=Template)
def update_template(template_id: int, template: Template, db: Session = Depends(get_db)):
    db_template = db.get(Template, template_id)
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    for key, value in template.model_dump(exclude_unset=True).items():
        setattr(db_template, key, value)
    
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template


@router.delete("/{template_id}")
def delete_template(template_id: int, db: Session = Depends(get_db)):
    template = db.get(Template, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Get all generations that use this template
    generations = db.exec(select(Generation).where(Generation.template_id == template_id)).all()
    
    # For each generation, we need to clean up related data
    for generation in generations:
        # 1. Update any questions that have this generation as selected_generation_id
        questions_with_selected = db.exec(
            select(Question).where(Question.selected_generation_id == generation.id)
        ).all()
        for question in questions_with_selected:
            question.selected_generation_id = None
            db.add(question)
        
        # 2. Delete all duels that involve this generation
        # First get all duels where this generation is a participant
        duel_generations = db.exec(
            select(DuelGeneration).where(DuelGeneration.generation_id == generation.id)
        ).all()
        
        # Get all duel IDs that involve this generation
        duel_ids = [dg.duel_id for dg in duel_generations]
        
        # Delete all DuelGeneration entries for these duels
        if duel_ids:
            # Delete DuelGeneration entries
            for duel_id in duel_ids:
                duel_gen_entries = db.exec(
                    select(DuelGeneration).where(DuelGeneration.duel_id == duel_id)
                ).all()
                for dg_entry in duel_gen_entries:
                    db.delete(dg_entry)
            
            # Delete the duels themselves
            for duel_id in duel_ids:
                duel = db.get(Duel, duel_id)
                if duel:
                    db.delete(duel)
        
        # 3. Delete the generation itself
        db.delete(generation)
    
    # 4. Finally, delete the template
    db.delete(template)
    db.commit()
    
    return {
        "message": f"Template deleted successfully along with {len(generations)} associated generations and their related data"
    }

