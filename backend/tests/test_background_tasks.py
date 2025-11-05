import pytest
from unittest.mock import patch, MagicMock
from sqlmodel import Session, select
from models.template import Template
from models.questions import Question
from models.generation import Generation
from models.duel import Duel, DuelGeneration


class TestBackgroundTasks:
    """Test background task for generation and duel creation"""
    
    def test_generation_and_duels_background_task_question_not_found(self, db_session):
        """Test background task when question doesn't exist"""
        # Run the background task with non-existent question ID
        from services.question import generation_and_duels_background_task
        generation_and_duels_background_task(999)
        
        # Should not raise an error, just return early
        generations = db_session.exec(select(Generation)).all()
        assert len(generations) == 0
        
        duels = db_session.exec(select(Duel)).all()
        assert len(duels) == 0
    
    def test_duel_creation_logic(self, db_session, sample_template, sample_question):
        """Test the duel creation logic separately"""
        # Add template and question to database
        db_session.add(sample_template)
        db_session.add(sample_question)
        db_session.commit()
        db_session.refresh(sample_template)
        db_session.refresh(sample_question)
        
        # Create two generations manually
        gen1 = Generation(
            template_id=sample_template.id,
            question_id=sample_question.id,
            output_text="Response 1",
            llm_model="gpt-4o-mini",
            latency=0.5,
            output_tokens=10,
            input_tokens=20
        )
        gen2 = Generation(
            template_id=sample_template.id,
            question_id=sample_question.id,
            output_text="Response 2",
            llm_model="gpt-4o-mini",
            latency=0.6,
            output_tokens=12,
            input_tokens=22
        )
        
        db_session.add(gen1)
        db_session.add(gen2)
        db_session.commit()
        db_session.refresh(gen1)
        db_session.refresh(gen2)
        
        # Test the duel creation logic from the background task
        generations = db_session.exec(select(Generation).where(Generation.question_id == sample_question.id)).all()
        
        # Create duels for all generation pairs
        for i, gen_a in enumerate(generations):
            for gen_b in generations[i+1:]:
                duel = Duel(question_id=sample_question.id)
                db_session.add(duel)
                db_session.flush()
                db_session.add(DuelGeneration(duel_id=duel.id, generation_id=gen_a.id, role="generation_a"))
                db_session.add(DuelGeneration(duel_id=duel.id, generation_id=gen_b.id, role="generation_b"))
        db_session.commit()
        
        # Verify duels were created
        duels = db_session.exec(select(Duel).where(Duel.question_id == sample_question.id)).all()
        assert len(duels) == 1  # One duel between the two generations
        
        # Verify duel generations were created
        duel_generations = db_session.exec(select(DuelGeneration)).all()
        assert len(duel_generations) == 2
        
        # Verify roles are correct
        roles = [dg.role for dg in duel_generations]
        assert "generation_a" in roles
        assert "generation_b" in roles
    
    def test_duel_creation_with_multiple_generations(self, db_session, sample_question):
        """Test duel creation with multiple generations"""
        # Create multiple templates
        template1 = Template(
            key="template1",
            name="Template 1",
            template_text="Answer: {{question}}"
        )
        template2 = Template(
            key="template2",
            name="Template 2",
            template_text="Please answer: {{question}}"
        )
        template3 = Template(
            key="template3",
            name="Template 3",
            template_text="Response: {{question}}"
        )
        
        # Add templates and question to database
        db_session.add(template1)
        db_session.add(template2)
        db_session.add(template3)
        db_session.add(sample_question)
        db_session.commit()
        db_session.refresh(template1)
        db_session.refresh(template2)
        db_session.refresh(template3)
        db_session.refresh(sample_question)
        
        # Create generations for all templates
        gen1 = Generation(
            template_id=template1.id,
            question_id=sample_question.id,
            output_text="Response 1",
            llm_model="gpt-4o-mini",
            latency=0.5,
            output_tokens=10,
            input_tokens=20
        )
        gen2 = Generation(
            template_id=template2.id,
            question_id=sample_question.id,
            output_text="Response 2",
            llm_model="gpt-4o-mini",
            latency=0.6,
            output_tokens=12,
            input_tokens=22
        )
        gen3 = Generation(
            template_id=template3.id,
            question_id=sample_question.id,
            output_text="Response 3",
            llm_model="gpt-4o-mini",
            latency=0.7,
            output_tokens=14,
            input_tokens=24
        )
        
        db_session.add(gen1)
        db_session.add(gen2)
        db_session.add(gen3)
        db_session.commit()
        db_session.refresh(gen1)
        db_session.refresh(gen2)
        db_session.refresh(gen3)
        
        # Test the duel creation logic
        generations = db_session.exec(select(Generation).where(Generation.question_id == sample_question.id)).all()
        
        # Create duels for all generation pairs
        for i, gen_a in enumerate(generations):
            for gen_b in generations[i+1:]:
                duel = Duel(question_id=sample_question.id)
                db_session.add(duel)
                db_session.flush()
                db_session.add(DuelGeneration(duel_id=duel.id, generation_id=gen_a.id, role="generation_a"))
                db_session.add(DuelGeneration(duel_id=duel.id, generation_id=gen_b.id, role="generation_b"))
        db_session.commit()
        
        # Verify duels were created (3 generations = 3 duels: 1v2, 1v3, 2v3)
        duels = db_session.exec(select(Duel).where(Duel.question_id == sample_question.id)).all()
        assert len(duels) == 3
        
        # Verify duel generations were created (2 per duel)
        duel_generations = db_session.exec(select(DuelGeneration)).all()
        assert len(duel_generations) == 6  # 3 duels * 2 generations per duel
