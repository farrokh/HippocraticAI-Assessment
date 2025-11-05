import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from models.template import Template
from models.questions import Question
from models.generation import Generation


class TestValidationErrors:
    """Test validation errors and error handling"""
    
    def test_create_question_invalid_field_type(self, client: TestClient):
        """Test creating a question with invalid field type"""
        response = client.post("/questions/", json={
            "text": 123  # Should be string
        })
        # Should either accept it or return validation error
        assert response.status_code in [200, 422]
    
    def test_update_question_invalid_id(self, client: TestClient):
        """Test updating a question with invalid ID type"""
        response = client.put("/questions/abc", json={
            "text": "Updated question"
        })
        assert response.status_code == 422  # Validation error for path parameter
    
    def test_update_template_invalid_id(self, client: TestClient):
        """Test updating a template with invalid ID type"""
        response = client.put("/templates/abc", json={
            "name": "Updated template"
        })
        assert response.status_code == 422  # Validation error for path parameter
    
    def test_delete_question_invalid_id(self, client: TestClient):
        """Test deleting a question with invalid ID type"""
        response = client.delete("/questions/abc")
        assert response.status_code == 422  # Validation error for path parameter
    
    def test_delete_template_invalid_id(self, client: TestClient):
        """Test deleting a template with invalid ID type"""
        response = client.delete("/templates/abc")
        assert response.status_code == 422  # Validation error for path parameter
    
    def test_get_question_invalid_id(self, client: TestClient):
        """Test getting a question with invalid ID type"""
        response = client.get("/questions/abc")
        assert response.status_code == 422  # Validation error for path parameter
    
    def test_get_template_invalid_id(self, client: TestClient):
        """Test getting a template with invalid ID type"""
        response = client.get("/templates/abc")
        assert response.status_code == 422  # Validation error for path parameter
    
    def test_decide_duel_missing_winner_id(self, client: TestClient):
        """Test deciding a duel without winner_id"""
        response = client.post("/questions/1/duels/1/decide", json={})
        assert response.status_code == 422  # Validation error
    
    def test_decide_duel_invalid_winner_id_type(self, client: TestClient):
        """Test deciding a duel with invalid winner_id type"""
        response = client.post("/questions/1/duels/1/decide", json={
            "winner_id": "not_a_number"
        })
        assert response.status_code == 422  # Validation error
    
    def test_get_questions_invalid_limit(self, client: TestClient):
        """Test getting questions with invalid limit parameter"""
        response = client.get("/questions/?limit=abc")
        assert response.status_code == 422  # Validation error
    
    def test_get_questions_negative_limit(self, client: TestClient):
        """Test getting questions with negative limit"""
        response = client.get("/questions/?limit=-1")
        # Should either reject negative limit or treat as 0
        assert response.status_code in [200, 422]
    
    def test_get_questions_zero_limit(self, client: TestClient):
        """Test getting questions with zero limit"""
        response = client.get("/questions/?limit=0")
        # Should either reject zero limit or return empty list
        assert response.status_code in [200, 422]
    
    def test_get_template_performance_invalid_overall_only(self, client: TestClient):
        """Test getting template performance with invalid overall_only parameter"""
        response = client.get("/templates/performance?overall_only=not_boolean")
        # Should either parse as boolean or return validation error
        assert response.status_code in [200, 422]
    
    def test_create_question_extra_fields(self, client: TestClient):
        """Test creating a question with extra unexpected fields"""
        response = client.post("/questions/", json={
            "text": "What is the capital of France?",
            "extra_field": "should be ignored or cause error"
        })
        # Should either ignore extra fields or return validation error
        assert response.status_code in [200, 422]
    
    def test_create_template_extra_fields(self, client: TestClient):
        """Test creating a template with extra unexpected fields"""
        response = client.post("/templates/", json={
            "key": "test_template",
            "name": "Test Template",
            "template_text": "Answer: {{question}}",
            "extra_field": "should be ignored or cause error"
        })
        # Should either ignore extra fields or return validation error
        assert response.status_code in [200, 422]

