import pytest
from sqlmodel import select
from models.template import Template
from models.questions import Question
from models.generation import Generation
from models.duel import Duel, DuelGeneration


class TestDatabaseModels:
    """Test database models and their relationships"""
    
    def test_template_creation(self, db_session, sample_template):
        """Test creating a template"""
        db_session.add(sample_template)
        db_session.commit()
        db_session.refresh(sample_template)
        
        assert sample_template.id is not None
        assert sample_template.key == "test_template"
        assert sample_template.name == "Test Template"
        assert sample_template.template_text == "Answer this question: {{question}}"
        assert sample_template.created_at is not None
    
    def test_question_creation(self, db_session, sample_question):
        """Test creating a question"""
        db_session.add(sample_question)
        db_session.commit()
        db_session.refresh(sample_question)
        
        assert sample_question.id is not None
        assert sample_question.text == "What is the capital of France?"
        assert sample_question.created_at is not None
        assert sample_question.selected_generation is None
    
    def test_generation_creation(self, db_session, sample_template, sample_question, sample_generation):
        """Test creating a generation"""
        # First add template and question
        db_session.add(sample_template)
        db_session.add(sample_question)
        db_session.commit()
        db_session.refresh(sample_template)
        db_session.refresh(sample_question)
        
        # Update generation with actual IDs
        sample_generation.template_id = sample_template.id
        sample_generation.question_id = sample_question.id
        
        db_session.add(sample_generation)
        db_session.commit()
        db_session.refresh(sample_generation)
        
        assert sample_generation.id is not None
        assert sample_generation.template_id == sample_template.id
        assert sample_generation.question_id == sample_question.id
        assert sample_generation.output_text == "The capital of France is Paris."
        assert sample_generation.llm_model == "gpt-4o-mini"
        assert sample_generation.latency == 0.5
        assert sample_generation.output_tokens == 10
        assert sample_generation.input_tokens == 20
    
    def test_duel_creation(self, db_session, sample_template, sample_question):
        """Test creating a duel"""
        # Create template and question
        db_session.add(sample_template)
        db_session.add(sample_question)
        db_session.commit()
        db_session.refresh(sample_template)
        db_session.refresh(sample_question)
        
        # Create two generations
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
        
        # Create duel
        duel = Duel(question_id=sample_question.id)
        db_session.add(duel)
        db_session.flush()  # Get the duel ID
        
        # Create duel generations
        duel_gen1 = DuelGeneration(
            duel_id=duel.id,
            generation_id=gen1.id,
            role="generation_a"
        )
        duel_gen2 = DuelGeneration(
            duel_id=duel.id,
            generation_id=gen2.id,
            role="generation_b"
        )
        
        db_session.add(duel_gen1)
        db_session.add(duel_gen2)
        db_session.commit()
        db_session.refresh(duel)
        
        assert duel.id is not None
        assert duel.question_id == sample_question.id
        assert duel.winner_id is None
        assert duel.created_at is not None
        assert duel.decided_at is None
    
    def test_question_generation_relationship(self, db_session, sample_template, sample_question):
        """Test the relationship between questions and generations"""
        # Create template and question
        db_session.add(sample_template)
        db_session.add(sample_question)
        db_session.commit()
        db_session.refresh(sample_template)
        db_session.refresh(sample_question)
        
        # Create generation
        generation = Generation(
            template_id=sample_template.id,
            question_id=sample_question.id,
            output_text="Test response",
            llm_model="gpt-4o-mini",
            latency=0.5,
            output_tokens=10,
            input_tokens=20
        )
        
        db_session.add(generation)
        db_session.commit()
        db_session.refresh(generation)
        
        # Test that we can query generations by question
        generations = db_session.exec(
            select(Generation).where(Generation.question_id == sample_question.id)
        ).all()
        
        assert len(generations) == 1
        assert generations[0].id == generation.id
        assert generations[0].question_id == sample_question.id
    
    def test_duel_generation_relationship(self, db_session, sample_template, sample_question):
        """Test the many-to-many relationship between duels and generations"""
        # Create template and question
        db_session.add(sample_template)
        db_session.add(sample_question)
        db_session.commit()
        db_session.refresh(sample_template)
        db_session.refresh(sample_question)
        
        # Create two generations
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
        
        # Create duel
        duel = Duel(question_id=sample_question.id)
        db_session.add(duel)
        db_session.flush()
        
        # Create duel generations
        duel_gen1 = DuelGeneration(
            duel_id=duel.id,
            generation_id=gen1.id,
            role="generation_a"
        )
        duel_gen2 = DuelGeneration(
            duel_id=duel.id,
            generation_id=gen2.id,
            role="generation_b"
        )
        
        db_session.add(duel_gen1)
        db_session.add(duel_gen2)
        db_session.commit()
        
        # Test that we can query duel generations
        duel_gens = db_session.exec(
            select(DuelGeneration).where(DuelGeneration.duel_id == duel.id)
        ).all()
        
        assert len(duel_gens) == 2
        roles = [dg.role for dg in duel_gens]
        assert "generation_a" in roles
        assert "generation_b" in roles
