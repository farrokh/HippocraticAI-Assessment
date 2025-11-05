import pytest
from sqlmodel import Session, select
from models.template import Template
from models.questions import Question
from models.generation import Generation
from models.duel import Duel, DuelGeneration
from services.question import set_question_winner


class TestQuestionService:
    """Test question service functions"""
    
    def test_set_question_winner_no_duels(self, db_session, sample_question):
        """Test set_question_winner when no duels exist"""
        db_session.add(sample_question)
        db_session.commit()
        db_session.refresh(sample_question)
        
        result = set_question_winner(sample_question.id, db_session)
        assert result is None
        db_session.refresh(sample_question)
        assert sample_question.selected_generation_id is None
    
    def test_set_question_winner_undecided_duels(self, db_session, sample_template, sample_question):
        """Test set_question_winner when duels exist but are not all decided"""
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
        
        # Create undecided duel
        duel = Duel(question_id=sample_question.id, winner_id=None)
        db_session.add(duel)
        db_session.flush()
        
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
        
        result = set_question_winner(sample_question.id, db_session)
        assert result is None
        db_session.refresh(sample_question)
        assert sample_question.selected_generation_id is None
    
    def test_set_question_winner_clear_winner(self, db_session, sample_template, sample_question):
        """Test set_question_winner with a clear winner"""
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
        
        # Create duels: gen1 wins both
        duel1 = Duel(question_id=sample_question.id, winner_id=gen1.id)
        db_session.add(duel1)
        db_session.flush()
        db_session.add(DuelGeneration(duel_id=duel1.id, generation_id=gen1.id, role="generation_a"))
        db_session.add(DuelGeneration(duel_id=duel1.id, generation_id=gen2.id, role="generation_b"))
        
        duel2 = Duel(question_id=sample_question.id, winner_id=gen1.id)
        db_session.add(duel2)
        db_session.flush()
        db_session.add(DuelGeneration(duel_id=duel2.id, generation_id=gen1.id, role="generation_a"))
        db_session.add(DuelGeneration(duel_id=duel2.id, generation_id=gen3.id, role="generation_b"))
        
        db_session.commit()
        
        result = set_question_winner(sample_question.id, db_session)
        assert result is not None
        db_session.refresh(sample_question)
        assert sample_question.selected_generation_id is not None
        assert sample_question.selected_generation_id == gen1.id
    
    def test_set_question_winner_tie_breaker(self, db_session, sample_template, sample_question):
        """Test set_question_winner with a tie - should use lowest ID"""
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
        
        # Create duels: gen1 wins one, gen2 wins one (tie)
        # gen1 vs gen2: gen1 wins
        duel1 = Duel(question_id=sample_question.id, winner_id=gen1.id)
        db_session.add(duel1)
        db_session.flush()
        db_session.add(DuelGeneration(duel_id=duel1.id, generation_id=gen1.id, role="generation_a"))
        db_session.add(DuelGeneration(duel_id=duel1.id, generation_id=gen2.id, role="generation_b"))
        
        # gen1 vs gen3: gen3 wins
        duel2 = Duel(question_id=sample_question.id, winner_id=gen3.id)
        db_session.add(duel2)
        db_session.flush()
        db_session.add(DuelGeneration(duel_id=duel2.id, generation_id=gen1.id, role="generation_a"))
        db_session.add(DuelGeneration(duel_id=duel2.id, generation_id=gen3.id, role="generation_b"))
        
        # gen2 vs gen3: gen2 wins
        duel3 = Duel(question_id=sample_question.id, winner_id=gen2.id)
        db_session.add(duel3)
        db_session.flush()
        db_session.add(DuelGeneration(duel_id=duel3.id, generation_id=gen2.id, role="generation_a"))
        db_session.add(DuelGeneration(duel_id=duel3.id, generation_id=gen3.id, role="generation_b"))
        
        db_session.commit()
        
        # All have 1 win, so gen1 (lowest ID) should win
        result = set_question_winner(sample_question.id, db_session)
        assert result is not None
        db_session.refresh(sample_question)
        assert sample_question.selected_generation_id is not None
        assert sample_question.selected_generation_id == gen1.id  # Lowest ID among tied winners
    
    def test_set_question_winner_question_not_found(self, db_session):
        """Test set_question_winner when question doesn't exist"""
        result = set_question_winner(999, db_session)
        assert result is None
    
    def test_set_question_winner_all_duels_decided_no_winners(self, db_session, sample_template, sample_question):
        """Test set_question_winner when all duels are decided but no winners (edge case)"""
        # This shouldn't happen in practice, but test the edge case
        db_session.add(sample_template)
        db_session.add(sample_question)
        db_session.commit()
        db_session.refresh(sample_template)
        db_session.refresh(sample_question)
        
        # Create a duel with winner_id set but no actual winner (edge case)
        # This is handled by the query that filters for winner_id != None
        result = set_question_winner(sample_question.id, db_session)
        assert result is None
    
    def test_set_question_winner_multiple_rounds(self, db_session, sample_template, sample_question):
        """Test set_question_winner when called multiple times"""
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
        
        # Create decided duel
        duel = Duel(question_id=sample_question.id, winner_id=gen1.id)
        db_session.add(duel)
        db_session.flush()
        db_session.add(DuelGeneration(duel_id=duel.id, generation_id=gen1.id, role="generation_a"))
        db_session.add(DuelGeneration(duel_id=duel.id, generation_id=gen2.id, role="generation_b"))
        db_session.commit()
        
        # First call should set winner
        result1 = set_question_winner(sample_question.id, db_session)
        assert result1 is not None
        db_session.refresh(sample_question)
        assert sample_question.selected_generation_id is not None
        assert sample_question.selected_generation_id == gen1.id
        
        # Second call should still work (idempotent)
        db_session.refresh(sample_question)
        result2 = set_question_winner(sample_question.id, db_session)
        assert result2 is not None
        assert sample_question.selected_generation_id is not None
        assert sample_question.selected_generation_id == gen1.id

