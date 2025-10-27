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
    
    # Single optimized query for per-question performance with template data
    question_query = select(
        Template,
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
        Template, Generation.template_id == Template.id
    ).join(
        Question, Duel.question_id == Question.id
    ).where(
        Duel.winner_id.isnot(None),
        Question.selected_generation_id.isnot(None)
    ).group_by(
        Template.id,
        Duel.question_id
    )
    
    # Execute question query
    question_results = db.exec(question_query).all()
    
    # Get all questions
    all_questions = {q.id: q for q in db.exec(select(Question)).all()}
    
    # Format per-question performance
    question_performance_map: Dict[int, List[Dict[str, Any]]] = {}
    
    for template, question_id, total_duels, wins in question_results:
        if question_id not in question_performance_map:
            question = all_questions.get(question_id)
            question_performance_map[question_id] = {
                "question_data": {
                    "question_id": question_id,
                    "question_text": question.text if question else f"Question {question_id}",
                    "template_performance": []
                }
            }
        
        win_rate = (wins / total_duels * 100) if total_duels > 0 else 0
        
        question_performance_map[question_id]["question_data"]["template_performance"].append({
            "template_id": template.id,
            "template_name": template.name,
            "template_key": template.key,
            "wins": wins,
            "total_duels": total_duels,
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
    generation_ids = [gen.id for gen in generations]
    
    if not generation_ids:
        # No generations to clean up, just delete template
        db.delete(template)
        db.commit()
        return {"message": "Template deleted successfully (no associated generations)"}
    
    # 1. Update questions that have any of these generations as selected_generation_id
    questions_to_update = db.exec(
        select(Question).where(Question.selected_generation_id.in_(generation_ids))
    ).all()
    for question in questions_to_update:
        question.selected_generation_id = None
        db.add(question)
    
    # 2. Get all duel IDs that involve any of these generations
    duel_generations = db.exec(
        select(DuelGeneration).where(DuelGeneration.generation_id.in_(generation_ids))
    ).all()
    duel_ids = list(set([dg.duel_id for dg in duel_generations]))
    
    # 3. Delete all DuelGeneration entries for these duels
    if duel_ids:
        # Delete all DuelGeneration entries for these duels
        duel_gen_entries = db.exec(
            select(DuelGeneration).where(DuelGeneration.duel_id.in_(duel_ids))
        ).all()
        for dg_entry in duel_gen_entries:
            db.delete(dg_entry)
        
        # Delete the duels themselves
        duels_to_delete = db.exec(select(Duel).where(Duel.id.in_(duel_ids))).all()
        for duel in duels_to_delete:
            db.delete(duel)
    
    # 4. Delete all generations
    for generation in generations:
        db.delete(generation)
    
    # 5. Finally, delete the template
    db.delete(template)
    db.commit()
    
    return {
        "message": f"Template deleted successfully along with {len(generations)} associated generations and their related data"
    }

