import pytest
from sqlmodel import Session, select
from models.template import Template
from models.questions import Question
from models.generation import Generation
from models.duel import Duel, DuelGeneration


class TestModelRelationships:
    """Test model relationships and edge cases"""
    
    def test_question_duels_relationship(self, db_session, sample_question):
        """Test the relationship between Question and Duel"""
        db_session.add(sample_question)
        db_session.commit()
        db_session.refresh(sample_question)
        
        # Create a duel
        duel = Duel(question_id=sample_question.id)
        db_session.add(duel)
        db_session.commit()
        db_session.refresh(duel)
        
        # Test relationship (if using selectin loading)
        # The relationship should be accessible
        assert duel.question_id == sample_question.id
    
    def test_question_selected_generation_relationship(self, db_session, sample_template, sample_question):
        """Test the relationship between Question and selected Generation via foreign key"""
        db_session.add(sample_template)
        db_session.add(sample_question)
        db_session.commit()
        db_session.refresh(sample_template)
        db_session.refresh(sample_question)
        
        # Create a generation
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
        
        # Set it as the selected generation
        sample_question.selected_generation_id = generation.id
        db_session.add(sample_question)
        db_session.commit()
        db_session.refresh(sample_question)
        
        assert sample_question.selected_generation_id == generation.id
    
    def test_duel_generations_many_to_many(self, db_session, sample_template, sample_question):
        """Test the many-to-many relationship between Duel and Generation"""
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
        
        # Test that we can query generations through the duel
        duel_generations = db_session.exec(
            select(DuelGeneration).where(DuelGeneration.duel_id == duel.id)
        ).all()
        assert len(duel_generations) == 2
        assert {dg.generation_id for dg in duel_generations} == {gen1.id, gen2.id}
    
    def test_generation_template_relationship(self, db_session, sample_template, sample_question):
        """Test the relationship between Generation and Template"""
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
        
        assert generation.template_id == sample_template.id
    
    def test_generation_question_relationship(self, db_session, sample_template, sample_question):
        """Test the relationship between Generation and Question"""
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
        
        assert generation.question_id == sample_question.id
    
    def test_duel_winner_relationship(self, db_session, sample_template, sample_question):
        """Test the relationship between Duel and winner Generation"""
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
        
        # Create duel with winner
        duel = Duel(question_id=sample_question.id, winner_id=generation.id)
        db_session.add(duel)
        db_session.commit()
        db_session.refresh(duel)
        
        assert duel.winner_id == generation.id
    
    def test_multiple_duels_same_question(self, db_session, sample_template, sample_question):
        """Test creating multiple duels for the same question"""
        db_session.add(sample_template)
        db_session.add(sample_question)
        db_session.commit()
        db_session.refresh(sample_template)
        db_session.refresh(sample_question)
        
        # Create three generations
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
        gen3 = Generation(
            template_id=sample_template.id,
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
        
        # Create multiple duels
        duel1 = Duel(question_id=sample_question.id)
        duel2 = Duel(question_id=sample_question.id)
        duel3 = Duel(question_id=sample_question.id)
        db_session.add(duel1)
        db_session.add(duel2)
        db_session.add(duel3)
        db_session.flush()
        
        # Create duel generations
        db_session.add(DuelGeneration(duel_id=duel1.id, generation_id=gen1.id, role="generation_a"))
        db_session.add(DuelGeneration(duel_id=duel1.id, generation_id=gen2.id, role="generation_b"))
        db_session.add(DuelGeneration(duel_id=duel2.id, generation_id=gen1.id, role="generation_a"))
        db_session.add(DuelGeneration(duel_id=duel2.id, generation_id=gen3.id, role="generation_b"))
        db_session.add(DuelGeneration(duel_id=duel3.id, generation_id=gen2.id, role="generation_a"))
        db_session.add(DuelGeneration(duel_id=duel3.id, generation_id=gen3.id, role="generation_b"))
        db_session.commit()
        
        # Verify all duels belong to the same question
        duels = db_session.exec(
            select(Duel).where(Duel.question_id == sample_question.id)
        ).all()
        assert len(duels) == 3
        assert all(duel.question_id == sample_question.id for duel in duels)
    
    def test_generation_with_multiple_duels(self, db_session, sample_template, sample_question):
        """Test a generation participating in multiple duels"""
        db_session.add(sample_template)
        db_session.add(sample_question)
        db_session.commit()
        db_session.refresh(sample_template)
        db_session.refresh(sample_question)
        
        # Create three generations
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
        gen3 = Generation(
            template_id=sample_template.id,
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
        
        # Create duels where gen1 participates in multiple
        duel1 = Duel(question_id=sample_question.id)
        duel2 = Duel(question_id=sample_question.id)
        db_session.add(duel1)
        db_session.add(duel2)
        db_session.flush()
        
        db_session.add(DuelGeneration(duel_id=duel1.id, generation_id=gen1.id, role="generation_a"))
        db_session.add(DuelGeneration(duel_id=duel1.id, generation_id=gen2.id, role="generation_b"))
        db_session.add(DuelGeneration(duel_id=duel2.id, generation_id=gen1.id, role="generation_a"))
        db_session.add(DuelGeneration(duel_id=duel2.id, generation_id=gen3.id, role="generation_b"))
        db_session.commit()
        
        # Verify gen1 is in multiple duels
        gen1_duels = db_session.exec(
            select(DuelGeneration).where(DuelGeneration.generation_id == gen1.id)
        ).all()
        assert len(gen1_duels) == 2
        assert {dg.duel_id for dg in gen1_duels} == {duel1.id, duel2.id}

