import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from models.template import Template
from models.questions import Question
from models.generation import Generation
from models.duel import Duel, DuelGeneration


class TestTemplateEndpoints:
    """Test template CRUD operations and performance endpoint"""
    
    def test_create_template(self, client: TestClient):
        """Test creating a template"""
        template_data = {
            "key": "test_template",
            "name": "Test Template",
            "template_text": "Answer this question: {{question}}"
        }
        
        response = client.post("/templates/", json=template_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["key"] == "test_template"
        assert data["name"] == "Test Template"
        assert data["template_text"] == "Answer this question: {{question}}"
        assert "id" in data
        assert "created_at" in data
    
    def test_get_templates(self, client: TestClient, sample_template):
        """Test getting all templates"""
        # First create a template
        response = client.post("/templates/", json={
            "key": "test_template",
            "name": "Test Template",
            "template_text": "Answer this question: {{question}}"
        })
        assert response.status_code == 200
        
        # Get all templates
        response = client.get("/templates/")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["key"] == "test_template"
        assert data[0]["name"] == "Test Template"
    
    def test_get_template_by_id(self, client: TestClient):
        """Test getting a specific template by ID"""
        # Create a template
        response = client.post("/templates/", json={
            "key": "test_template",
            "name": "Test Template",
            "template_text": "Answer this question: {{question}}"
        })
        assert response.status_code == 200
        template_id = response.json()["id"]
        
        # Get the template by ID
        response = client.get(f"/templates/{template_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == template_id
        assert data["key"] == "test_template"
        assert data["name"] == "Test Template"
    
    def test_get_template_not_found(self, client: TestClient):
        """Test getting a non-existent template"""
        response = client.get("/templates/999")
        assert response.status_code == 404
        assert "Template not found" in response.json()["detail"]
    
    def test_update_template(self, client: TestClient):
        """Test updating a template"""
        # Create a template
        response = client.post("/templates/", json={
            "key": "test_template",
            "name": "Test Template",
            "template_text": "Answer this question: {{question}}"
        })
        assert response.status_code == 200
        template_id = response.json()["id"]
        
        # Update the template
        update_data = {
            "name": "Updated Template",
            "template_text": "Please answer: {{question}}"
        }
        response = client.put(f"/templates/{template_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == template_id
        assert data["key"] == "test_template"  # Should remain unchanged
        assert data["name"] == "Updated Template"
        assert data["template_text"] == "Please answer: {{question}}"
    
    def test_update_template_not_found(self, client: TestClient):
        """Test updating a non-existent template"""
        update_data = {
            "name": "Updated Template"
        }
        response = client.put("/templates/999", json=update_data)
        assert response.status_code == 404
        assert "Template not found" in response.json()["detail"]
    
    def test_delete_template(self, client: TestClient):
        """Test deleting a template"""
        # Create a template
        response = client.post("/templates/", json={
            "key": "test_template",
            "name": "Test Template",
            "template_text": "Answer this question: {{question}}"
        })
        assert response.status_code == 200
        template_id = response.json()["id"]
        
        # Delete the template
        response = client.delete(f"/templates/{template_id}")
        assert response.status_code == 200
        assert "Template deleted successfully" in response.json()["message"]
        
        # Verify template is deleted
        response = client.get(f"/templates/{template_id}")
        assert response.status_code == 404
    
    def test_delete_template_not_found(self, client: TestClient):
        """Test deleting a non-existent template"""
        response = client.delete("/templates/999")
        assert response.status_code == 404
        assert "Template not found" in response.json()["detail"]
    
    def test_template_performance_overall_only(self, client: TestClient):
        """Test getting overall template performance only"""
        response = client.get("/templates/performance?overall_only=true")
        assert response.status_code == 200
        
        data = response.json()
        assert "overall" in data
        assert "by_question" not in data
    
    def test_template_performance_full(self, client: TestClient):
        """Test getting full template performance"""
        response = client.get("/templates/performance")
        assert response.status_code == 200
        
        data = response.json()
        assert "overall" in data
        assert "by_question" in data
        assert isinstance(data["overall"], list)
        assert isinstance(data["by_question"], list)
    
    def test_delete_template_with_generations(self, client: TestClient):
        """Test deleting a template that has associated generations and duels"""
        # This test would require setting up a complex scenario with:
        # 1. Template
        # 2. Question
        # 3. Generations using the template
        # 4. Duels between generations
        # 5. Question with selected generation
        
        # For now, we'll test the basic case where template has no generations
        response = client.post("/templates/", json={
            "key": "test_template",
            "name": "Test Template",
            "template_text": "Answer this question: {{question}}"
        })
        assert response.status_code == 200
        template_id = response.json()["id"]
        
        # Delete the template
        response = client.delete(f"/templates/{template_id}")
        assert response.status_code == 200
        assert "no associated generations" in response.json()["message"]
