import pytest
from sqlmodel import Session, select
from models.template import Template
from models.questions import Question
from models.generation import Generation
from models.duel import Duel, DuelGeneration
from services.performance import get_generation_performance_stats, get_template_performance_stats
from services.question import set_question_winner


class TestPerformanceService:
    """Test performance calculation services"""
    
    def test_get_generation_performance_stats_no_duels(self, db_session, sample_template, sample_question):
        """Test generation performance stats when no duels exist"""
        # Add template and question to database
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
        
        # Get performance stats
        stats = get_generation_performance_stats(sample_question.id, db_session)
        
        # Should return empty list since no duels exist
        assert len(stats) == 0
    
    def test_get_generation_performance_stats_with_duels(self, db_session, sample_template, sample_question):
        """Test generation performance stats with completed duels"""
        # Add template and question to database
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
        
        # Create a duel
        duel = Duel(question_id=sample_question.id, winner_id=gen1.id)
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
        
        # Get performance stats
        stats = get_generation_performance_stats(sample_question.id, db_session)
        
        # Should return stats for both generations
        assert len(stats) == 2
        
        # Find the winner (gen1)
        winner_stats = next(s for s in stats if s["generation_id"] == gen1.id)
        assert winner_stats["wins"] == 1
        assert winner_stats["total_duels"] == 1
        assert winner_stats["win_rate"] == 100.0
        
        # Find the loser (gen2)
        loser_stats = next(s for s in stats if s["generation_id"] == gen2.id)
        assert loser_stats["wins"] == 0
        assert loser_stats["total_duels"] == 1
        assert loser_stats["win_rate"] == 0.0
        
        # Verify template data is included
        assert winner_stats["template_id"] == sample_template.id
        assert winner_stats["template_name"] == sample_template.name
        assert winner_stats["template_key"] == sample_template.key
    
    def test_get_template_performance_stats_no_data(self, db_session):
        """Test template performance stats when no data exists"""
        stats = get_template_performance_stats(db_session)
        
        assert "overall" in stats
        assert len(stats["overall"]) == 0
    
    def test_get_template_performance_stats_with_data(self, db_session, sample_template, sample_question):
        """Test template performance stats with completed duels"""
        # Add template and question to database
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
        
        # Create a duel
        duel = Duel(question_id=sample_question.id, winner_id=gen1.id)
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
        
        # Set question winner (required for template performance stats)
        gen1.is_selected = True
        db_session.add(gen1)
        db_session.commit()
        
        # Get template performance stats
        stats = get_template_performance_stats(db_session)
        
        assert "overall" in stats
        assert len(stats["overall"]) == 1
        
        template_stats = stats["overall"][0]
        assert template_stats["template_id"] == sample_template.id
        assert template_stats["template_name"] == sample_template.name
        assert template_stats["template_key"] == sample_template.key
        assert template_stats["wins"] == 1
        # The total_duels count includes all duels where this template participated
        # Since both generations use the same template, it appears in 2 duels (as generation_a and generation_b)
        assert template_stats["total_duels"] == 2
        assert template_stats["win_rate"] == 50.0  # 1 win out of 2 total duels
    
    def test_get_template_performance_stats_filtered_by_question(self, db_session):
        """Test template performance stats filtered by question ID"""
        # Create two templates
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
        
        # Create two questions
        question1 = Question(text="Question 1")
        question2 = Question(text="Question 2")
        
        # Add to database
        db_session.add(template1)
        db_session.add(template2)
        db_session.add(question1)
        db_session.add(question2)
        db_session.commit()
        db_session.refresh(template1)
        db_session.refresh(template2)
        db_session.refresh(question1)
        db_session.refresh(question2)
        
        # Create generations for both templates and questions
        gen1_q1 = Generation(
            template_id=template1.id,
            question_id=question1.id,
            output_text="Response 1",
            llm_model="gpt-4o-mini",
            latency=0.5,
            output_tokens=10,
            input_tokens=20
        )
        gen2_q1 = Generation(
            template_id=template2.id,
            question_id=question1.id,
            output_text="Response 2",
            llm_model="gpt-4o-mini",
            latency=0.6,
            output_tokens=12,
            input_tokens=22
        )
        gen1_q2 = Generation(
            template_id=template1.id,
            question_id=question2.id,
            output_text="Response 3",
            llm_model="gpt-4o-mini",
            latency=0.5,
            output_tokens=10,
            input_tokens=20
        )
        
        db_session.add(gen1_q1)
        db_session.add(gen2_q1)
        db_session.add(gen1_q2)
        db_session.commit()
        db_session.refresh(gen1_q1)
        db_session.refresh(gen2_q1)
        db_session.refresh(gen1_q2)
        
        # Create duels for question 1
        duel1 = Duel(question_id=question1.id, winner_id=gen1_q1.id)
        db_session.add(duel1)
        db_session.flush()
        
        duel_gen1 = DuelGeneration(
            duel_id=duel1.id,
            generation_id=gen1_q1.id,
            role="generation_a"
        )
        duel_gen2 = DuelGeneration(
            duel_id=duel1.id,
            generation_id=gen2_q1.id,
            role="generation_b"
        )
        
        db_session.add(duel_gen1)
        db_session.add(duel_gen2)
        db_session.commit()
        
        # Set question 1 winner
        gen1_q1.is_selected = True
        db_session.add(gen1_q1)
        db_session.commit()
        
        # Get template performance stats filtered by question 1
        stats = get_template_performance_stats(db_session, question_id=question1.id)
        
        assert "overall" in stats
        assert len(stats["overall"]) == 2  # Both templates participated in question 1
        
        # Verify template 1 won
        template1_stats = next(s for s in stats["overall"] if s["template_id"] == template1.id)
        assert template1_stats["wins"] == 1
        assert template1_stats["total_duels"] == 1
        assert template1_stats["win_rate"] == 100.0
        
        # Verify template 2 lost
        template2_stats = next(s for s in stats["overall"] if s["template_id"] == template2.id)
        assert template2_stats["wins"] == 0
        assert template2_stats["total_duels"] == 1
        assert template2_stats["win_rate"] == 0.0
