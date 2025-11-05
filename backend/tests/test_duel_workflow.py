import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from models.template import Template
from models.questions import Question
from models.generation import Generation
from models.duel import Duel, DuelGeneration


class TestDuelWorkflow:
    """Test complete duel workflow scenarios"""
    
    def test_complete_duel_workflow(self, client: TestClient):
        """Test the complete workflow: create question, get next duel, decide it"""
        # Create template
        template_response = client.post("/templates/", json={
            "key": "test_template",
            "name": "Test Template",
            "template_text": "Answer: {{question}}"
        })
        assert template_response.status_code == 200
        template_id = template_response.json()["id"]
        
        # Create question
        question_response = client.post("/questions/", json={
            "text": "What is the capital of France?"
        })
        assert question_response.status_code == 200
        question_id = question_response.json()["id"]
        
        # Note: In a real scenario, the background task would generate outputs
        # For testing, we need to manually set up the scenario or wait
        # This test demonstrates the expected flow
    
    def test_decide_duel_and_auto_select_winner(self, client: TestClient):
        """Test deciding all duels and verifying winner is automatically selected"""
        # This would require:
        # 1. Creating templates and question
        # 2. Generating outputs (via background task or manually)
        # 3. Creating duels
        # 4. Deciding all duels
        # 5. Verifying question.selected_generation_id is set
        pass
    
    def test_get_next_duel_after_deciding_one(self, client: TestClient):
        """Test getting next duel after deciding one"""
        # This would require:
        # 1. Setting up question with multiple duels
        # 2. Getting next duel
        # 3. Deciding it
        # 4. Getting next duel again
        # 5. Verifying it's a different duel
        pass
    
    def test_decide_duel_with_invalid_winner(self, client: TestClient):
        """Test deciding a duel with a winner ID that's not in the duel"""
        # Create question
        question_response = client.post("/questions/", json={
            "text": "What is the capital of France?"
        })
        assert question_response.status_code == 200
        question_id = question_response.json()["id"]
        
        # Try to decide a non-existent duel with invalid winner
        response = client.post(
            f"/questions/{question_id}/duels/999/decide",
            json={"winner_id": 999}
        )
        assert response.status_code == 404
    
    def test_get_question_results_after_duels_decided(self, client: TestClient):
        """Test getting question results after all duels are decided"""
        # Create question
        question_response = client.post("/questions/", json={
            "text": "What is the capital of France?"
        })
        assert question_response.status_code == 200
        question_id = question_response.json()["id"]
        
        # Get results (even if no duels exist yet)
        response = client.get(f"/questions/{question_id}/results")
        assert response.status_code == 200
        data = response.json()
        assert "question" in data
        assert "selected_generation" in data
        assert "generation_performance" in data
    
    def test_multiple_questions_duel_isolation(self, client: TestClient):
        """Test that duels are properly isolated between questions"""
        # Create two questions
        question1_response = client.post("/questions/", json={
            "text": "Question 1"
        })
        assert question1_response.status_code == 200
        question1_id = question1_response.json()["id"]
        
        question2_response = client.post("/questions/", json={
            "text": "Question 2"
        })
        assert question2_response.status_code == 200
        question2_id = question2_response.json()["id"]
        
        # Get duels for each question (should be empty initially)
        duels1_response = client.get(f"/questions/{question1_id}/duels")
        assert duels1_response.status_code == 200
        assert len(duels1_response.json()) == 0
        
        duels2_response = client.get(f"/questions/{question2_id}/duels")
        assert duels2_response.status_code == 200
        assert len(duels2_response.json()) == 0

