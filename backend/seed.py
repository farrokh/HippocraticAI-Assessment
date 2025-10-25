from sqlmodel import Session, select
from db import engine
from models.template import Template

TEMPLATES = [
    {"key": "direct", "name": "Direct",
        "template_text": "Answer succinctly: {{question}}"},
    {"key": "cot_light", "name": "Reason+Answer",
        "template_text": "In one short sentence explain your reasoning, then answer: {{question}}"},
    {"key": "expert_cot", "name": "Expert Reason+Answer",
        "template_text": "Consider responding to the question as an expert of the topic. Answer succinctly: {{question}}"},
    {"key": "expert_guarded", "name": "Expert Guarded",
        "template_text": "If uncertain, say so briefly; then answer clearly: {{question}}"},
]


def seed_templates():
    """Seed templates into the database"""
    with Session(engine) as session:
        for template_data in TEMPLATES:
            # Check if template already exists
            existing = session.exec(
                select(Template).where(Template.key == template_data["key"])
            ).first()
            
            if not existing:
                template = Template(**template_data)
                session.add(template)
                print(f"✓ Created template: {template_data['name']}")
            else:
                print(f"⊘ Template already exists: {template_data['name']}")
        
        session.commit()
        print("\n✨ Seeding complete!")


if __name__ == "__main__":
    seed_templates()

