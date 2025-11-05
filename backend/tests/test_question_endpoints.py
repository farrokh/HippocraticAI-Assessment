import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from models.template import Template
from models.questions import Question
from models.generation import Generation
from models.duel import Duel, DuelGeneration


class TestQuestionEndpoints:
    """Test question CRUD operations and duel management"""
    
    def test_create_question(self, client: TestClient):
        """Test creating a question"""
        question_data = {
            "text": "What is the capital of France?"
        }
        
        response = client.post("/questions/", json=question_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["text"] == "What is the capital of France?"
        assert "id" in data
        assert "created_at" in data
    
    def test_get_questions(self, client: TestClient):
        """Test getting all questions"""
        # Create a question
        response = client.post("/questions/", json={
            "text": "What is the capital of France?"
        })
        assert response.status_code == 200
        
        # Get all questions
        response = client.get("/questions/")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["text"] == "What is the capital of France?"
        assert data[0]["selected_generation"] is None
    
    def test_get_questions_with_details(self, client: TestClient):
        """Test getting questions with generation details"""
        # Create a question
        response = client.post("/questions/", json={
            "text": "What is the capital of France?"
        })
        assert response.status_code == 200
        
        # Get questions with details
        response = client.get("/questions/?details=true")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["text"] == "What is the capital of France?"
        assert data[0]["selected_generation"] is None  # No selected generation yet
    
    def test_get_question_by_id(self, client: TestClient):
        """Test getting a specific question by ID"""
        # Create a question
        response = client.post("/questions/", json={
            "text": "What is the capital of France?"
        })
        assert response.status_code == 200
        question_id = response.json()["id"]
        
        # Get the question by ID
        response = client.get(f"/questions/{question_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == question_id
        assert data["text"] == "What is the capital of France?"
    
    def test_get_question_not_found(self, client: TestClient):
        """Test getting a non-existent question"""
        response = client.get("/questions/999")
        assert response.status_code == 404
        assert "Question not found" in response.json()["detail"]
    
    def test_update_question(self, client: TestClient):
        """Test updating a question"""
        # Create a question
        response = client.post("/questions/", json={
            "text": "What is the capital of France?"
        })
        assert response.status_code == 200
        question_id = response.json()["id"]
        
        # Update the question
        update_data = {
            "text": "What is the capital of Germany?"
        }
        response = client.put(f"/questions/{question_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == question_id
        assert data["text"] == "What is the capital of Germany?"
    
    def test_update_question_not_found(self, client: TestClient):
        """Test updating a non-existent question"""
        update_data = {
            "text": "Updated question"
        }
        response = client.put("/questions/999", json=update_data)
        assert response.status_code == 404
        assert "Question not found" in response.json()["detail"]
    
    def test_delete_question(self, client: TestClient):
        """Test deleting a question"""
        # Create a question
        response = client.post("/questions/", json={
            "text": "What is the capital of France?"
        })
        assert response.status_code == 200
        question_id = response.json()["id"]
        
        # Delete the question
        response = client.delete(f"/questions/{question_id}")
        assert response.status_code == 200
        assert "Question deleted successfully" in response.json()["message"]
        
        # Verify question is deleted
        response = client.get(f"/questions/{question_id}")
        assert response.status_code == 404
    
    def test_delete_question_not_found(self, client: TestClient):
        """Test deleting a non-existent question"""
        response = client.delete("/questions/999")
        assert response.status_code == 404
        assert "Question not found" in response.json()["detail"]
    
    def test_get_duels_by_question(self, client: TestClient):
        """Test getting duels for a question"""
        # Create a question
        response = client.post("/questions/", json={
            "text": "What is the capital of France?"
        })
        assert response.status_code == 200
        question_id = response.json()["id"]
        
        # Get duels for the question (should be empty initially)
        response = client.get(f"/questions/{question_id}/duels")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0  # No duels created yet
    
    def test_get_next_duel_no_duels(self, client: TestClient):
        """Test getting next duel when no duels exist"""
        # Create a question
        response = client.post("/questions/", json={
            "text": "What is the capital of France?"
        })
        assert response.status_code == 200
        question_id = response.json()["id"]
        
        # Try to get next duel - should return 202 (still processing) not 404
        response = client.get(f"/questions/{question_id}/duels/next")
        assert response.status_code == 202
        # Check that we get a processing message
        detail = response.json()["detail"]
        assert "processing" in detail.lower() or "processed" in detail.lower()
    
    def test_decide_duel_not_found(self, client: TestClient):
        """Test deciding a non-existent duel"""
        decide_data = {
            "winner_id": 1
        }
        response = client.post("/questions/1/duels/999/decide", json=decide_data)
        assert response.status_code == 404
        assert "Duel not found" in response.json()["detail"]
    
    def test_get_question_results(self, client: TestClient):
        """Test getting question results"""
        # Create a question
        response = client.post("/questions/", json={
            "text": "What is the capital of France?"
        })
        assert response.status_code == 200
        question_id = response.json()["id"]
        
        # Get question results
        response = client.get(f"/questions/{question_id}/results")
        assert response.status_code == 200
        
        data = response.json()
        assert "question" in data
        assert "selected_generation" in data
        assert "generation_performance" in data
        assert data["question"]["id"] == question_id
        assert data["selected_generation"] is None  # No selected generation yet
        assert isinstance(data["generation_performance"], list)
    
    def test_get_question_results_not_found(self, client: TestClient):
        """Test getting results for a non-existent question"""
        response = client.get("/questions/999/results")
        assert response.status_code == 404
        assert "Question not found" in response.json()["detail"]
