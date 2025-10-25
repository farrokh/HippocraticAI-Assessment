from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from models.template import Template
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
    
    db.delete(template)
    db.commit()
    return {"message": "Template deleted successfully"}

