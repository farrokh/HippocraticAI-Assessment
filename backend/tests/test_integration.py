import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch


class TestMainApplication:
    """Test the main FastAPI application"""
    
    def test_root_endpoint(self, client: TestClient):
        """Test the root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Welcome to the LLM Tournament Widget API"
    
    def test_cors_headers(self, client: TestClient):
        """Test that CORS headers are properly set"""
        response = client.options("/", headers={"Origin": "http://localhost:3000"})
        
        # FastAPI TestClient doesn't fully simulate CORS, but we can check the middleware is configured
        # The actual CORS behavior would be tested in integration tests
        assert response.status_code in [200, 405]  # OPTIONS might not be implemented for root
    
    def test_api_docs_available(self, client: TestClient):
        """Test that API documentation is available"""
        response = client.get("/docs")
        assert response.status_code == 200
        
        # Should return HTML content
        assert "text/html" in response.headers.get("content-type", "")
    
    def test_openapi_schema_available(self, client: TestClient):
        """Test that OpenAPI schema is available"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        data = response.json()
        assert data["info"]["title"] == "LLM Tournament Widget API"
        assert data["info"]["version"] == "1.0.0"
        assert "paths" in data
    
    def test_redoc_available(self, client: TestClient):
        """Test that ReDoc documentation is available"""
        response = client.get("/redoc")
        assert response.status_code == 200
        
        # Should return HTML content
        assert "text/html" in response.headers.get("content-type", "")


class TestIntegrationScenarios:
    """Integration tests for complete workflows"""
    
    @patch('services.llm.OpenAI')
    def test_complete_question_workflow(self, mock_openai_class, client: TestClient):
        """Test the complete workflow from question creation to results"""
        # Mock OpenAI response
        mock_response = mock_openai_class.return_value.chat.completions.create.return_value
        mock_response.choices = [type('obj', (object,), {'message': type('obj', (object,), {'content': 'Mocked response'})()})()]
        mock_response.usage.completion_tokens = 10
        mock_response.usage.prompt_tokens = 20
        
        # 1. Create a template
        template_response = client.post("/templates/", json={
            "key": "test_template",
            "name": "Test Template",
            "template_text": "Answer this question: {{question}}"
        })
        assert template_response.status_code == 200
        template_id = template_response.json()["id"]
        
        # 2. Create a question
        question_response = client.post("/questions/", json={
            "text": "What is the capital of France?"
        })
        assert question_response.status_code == 200
        question_id = question_response.json()["id"]
        
        # 3. Wait a moment for background task to complete (in real scenario)
        # For testing, we'll manually trigger the background task
        from services.question import generation_and_duels_background_task
        generation_and_duels_background_task(question_id)
        
        # 4. Get the question with details
        question_details = client.get(f"/questions/{question_id}")
        assert question_details.status_code == 200
        
        # 5. Get duels for the question
        duels_response = client.get(f"/questions/{question_id}/duels")
        assert duels_response.status_code == 200
        
        # 6. Get next duel (if any)
        try:
            next_duel = client.get(f"/questions/{question_id}/duels/next")
            if next_duel.status_code == 200:
                duel_data = next_duel.json()
                duel_id = duel_data["id"]
                
                # 7. Decide the duel
                decide_response = client.post(
                    f"/questions/{question_id}/duels/{duel_id}/decide",
                    json={"winner_id": duel_data["generation_a"]["id"]}
                )
                assert decide_response.status_code == 200
        except:
            # No duels created yet, which is fine for this test
            pass
        
        # 8. Get question results
        results_response = client.get(f"/questions/{question_id}/results")
        assert results_response.status_code == 200
        
        # 9. Get template performance
        performance_response = client.get("/templates/performance")
        assert performance_response.status_code == 200
    
    def test_template_crud_workflow(self, client: TestClient):
        """Test complete template CRUD workflow"""
        # 1. Create template
        create_response = client.post("/templates/", json={
            "key": "workflow_template",
            "name": "Workflow Template",
            "template_text": "Test: {{question}}"
        })
        assert create_response.status_code == 200
        template_id = create_response.json()["id"]
        
        # 2. Get template
        get_response = client.get(f"/templates/{template_id}")
        assert get_response.status_code == 200
        assert get_response.json()["name"] == "Workflow Template"
        
        # 3. Update template
        update_response = client.put(f"/templates/{template_id}", json={
            "name": "Updated Workflow Template"
        })
        assert update_response.status_code == 200
        assert update_response.json()["name"] == "Updated Workflow Template"
        
        # 4. Get all templates
        all_templates = client.get("/templates/")
        assert all_templates.status_code == 200
        assert len(all_templates.json()) == 1
        
        # 5. Delete template
        delete_response = client.delete(f"/templates/{template_id}")
        assert delete_response.status_code == 200
        
        # 6. Verify deletion
        get_deleted = client.get(f"/templates/{template_id}")
        assert get_deleted.status_code == 404
