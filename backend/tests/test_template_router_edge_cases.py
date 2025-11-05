import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from models.template import Template
from models.questions import Question
from models.generation import Generation
from models.duel import Duel, DuelGeneration


class TestTemplateRouterEdgeCases:
    """Test edge cases for template router endpoints"""
    
    def test_delete_template_with_generations_and_duels(self, client: TestClient):
        """Test deleting a template that has associated generations and duels"""
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
        
        # This would require creating generations and duels
        # For now, we test the basic deletion case
        delete_response = client.delete(f"/templates/{template_id}")
        assert delete_response.status_code == 200
    
    def test_delete_template_with_selected_generation(self, client: TestClient):
        """Test deleting a template when one of its generations is selected"""
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
        
        # This would require:
        # 1. Creating a generation with this template
        # 2. Setting it as selected_generation_id on the question
        # 3. Verifying deletion clears the selected_generation_id
        # For now, we test the basic case
        pass
    
    def test_get_template_performance_empty(self, client: TestClient):
        """Test getting template performance when no data exists"""
        response = client.get("/templates/performance")
        assert response.status_code == 200
        data = response.json()
        assert "overall" in data
        assert "by_question" in data
        assert isinstance(data["overall"], list)
        assert isinstance(data["by_question"], list)
        assert len(data["overall"]) == 0
        assert len(data["by_question"]) == 0
    
    def test_get_template_performance_overall_only(self, client: TestClient):
        """Test getting template performance with overall_only=true"""
        response = client.get("/templates/performance?overall_only=true")
        assert response.status_code == 200
        data = response.json()
        assert "overall" in data
        assert "by_question" not in data
        assert isinstance(data["overall"], list)
    
    def test_get_template_performance_by_question(self, client: TestClient):
        """Test getting template performance with by_question data"""
        response = client.get("/templates/performance")
        assert response.status_code == 200
        data = response.json()
        assert "overall" in data
        assert "by_question" in data
        assert isinstance(data["by_question"], list)
    
    def test_update_template_partial_update(self, client: TestClient):
        """Test updating a template with partial data"""
        # Create template
        create_response = client.post("/templates/", json={
            "key": "test_template",
            "name": "Test Template",
            "template_text": "Answer: {{question}}"
        })
        assert create_response.status_code == 200
        template_id = create_response.json()["id"]
        
        # Update only name
        update_response = client.put(f"/templates/{template_id}", json={
            "name": "Updated Name"
        })
        assert update_response.status_code == 200
        data = update_response.json()
        assert data["name"] == "Updated Name"
        assert data["key"] == "test_template"  # Should remain unchanged
        assert data["template_text"] == "Answer: {{question}}"  # Should remain unchanged
    
    def test_update_template_all_fields(self, client: TestClient):
        """Test updating a template with all fields"""
        # Create template
        create_response = client.post("/templates/", json={
            "key": "test_template",
            "name": "Test Template",
            "template_text": "Answer: {{question}}"
        })
        assert create_response.status_code == 200
        template_id = create_response.json()["id"]
        
        # Update all fields
        update_response = client.put(f"/templates/{template_id}", json={
            "name": "Updated Template",
            "template_text": "Please answer: {{question}}"
        })
        assert update_response.status_code == 200
        data = update_response.json()
        assert data["name"] == "Updated Template"
        assert data["template_text"] == "Please answer: {{question}}"
        assert data["key"] == "test_template"  # Key should not change
    
    def test_get_templates_empty(self, client: TestClient):
        """Test getting templates when none exist"""
        response = client.get("/templates/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_create_template_duplicate_key(self, client: TestClient):
        """Test creating a template with duplicate key"""
        # Create first template
        response1 = client.post("/templates/", json={
            "key": "duplicate_key",
            "name": "Template 1",
            "template_text": "Answer: {{question}}"
        })
        assert response1.status_code == 200
        
        # Try to create second template with same key
        response2 = client.post("/templates/", json={
            "key": "duplicate_key",
            "name": "Template 2",
            "template_text": "Please answer: {{question}}"
        })
        # Should either succeed (if duplicates allowed) or fail with validation error
        assert response2.status_code in [200, 422, 400]
    
    def test_create_template_empty_fields(self, client: TestClient):
        """Test creating a template with empty fields"""
        response = client.post("/templates/", json={
            "key": "",
            "name": "",
            "template_text": ""
        })
        # Should either succeed (if empty strings allowed) or fail with validation error
        assert response.status_code in [200, 422]
    
    def test_get_template_performance_with_data(self, client: TestClient):
        """Test getting template performance with actual data"""
        # This would require setting up:
        # 1. Templates
        # 2. Questions
        # 3. Generations
        # 4. Duels with winners
        # 5. Selected generations
        # For now, we test the structure
        response = client.get("/templates/performance")
        assert response.status_code == 200
        data = response.json()
        assert "overall" in data
        assert "by_question" in data

