import pytest
from unittest.mock import patch, MagicMock
from models.template import Template
from models.questions import Question
from models.generation import Generation
from services.llm import render_template, generate_output, generate_outputs


class TestLLMService:
    """Test LLM service with mocked OpenAI responses"""
    
    def test_render_template(self):
        """Test template rendering with question substitution"""
        template = Template(
            key="test_template",
            name="Test Template",
            template_text="Answer this question: {{question}}"
        )
        question = Question(text="What is the capital of France?")
        
        result = render_template(template, question)
        expected = "Answer this question: What is the capital of France?"
        assert result == expected
    
    def test_render_template_no_substitution(self):
        """Test template rendering when no substitution is needed"""
        template = Template(
            key="test_template",
            name="Test Template",
            template_text="This is a static template"
        )
        question = Question(text="What is the capital of France?")
        
        result = render_template(template, question)
        assert result == "This is a static template"
    
    @patch('services.llm.OpenAI')
    def test_generate_output(self, mock_openai_class, mock_openai_response):
        """Test generating output from a single template"""
        # Setup mock
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_openai_response
        mock_openai_class.return_value = mock_client
        
        template = Template(
            key="test_template",
            name="Test Template",
            template_text="Answer this question: {{question}}"
        )
        question = Question(text="What is the capital of France?")
        
        result = generate_output(template, question, mock_client)
        
        # Verify the result structure
        assert "output_text" in result
        assert "latency" in result
        assert "output_tokens" in result
        assert "input_tokens" in result
        assert "llm_model" in result
        
        # Verify values
        assert result["output_text"] == "Mocked response"
        assert result["latency"] == 10 / 150  # completion_tokens / 150
        assert result["output_tokens"] == 10
        assert result["input_tokens"] == 20
        assert result["llm_model"] == "gpt-4o-mini"
        
        # Verify OpenAI was called correctly
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]["model"] == "gpt-4o-mini"
        assert len(call_args[1]["messages"]) == 1
        assert call_args[1]["messages"][0]["role"] == "user"
        assert "What is the capital of France?" in call_args[1]["messages"][0]["content"]
    
    @patch('services.llm.OpenAI')
    def test_generate_output_without_client(self, mock_openai_class, mock_openai_response):
        """Test generating output without providing a client"""
        # Setup mock
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_openai_response
        mock_openai_class.return_value = mock_client
        
        template = Template(
            key="test_template",
            name="Test Template",
            template_text="Answer this question: {{question}}"
        )
        question = Question(text="What is the capital of France?")
        
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            result = generate_output(template, question)
        
        assert result["output_text"] == "Mocked response"
        mock_openai_class.assert_called_once_with(api_key='test-key')
    
    def test_generate_output_no_api_key(self):
        """Test generating output without API key"""
        template = Template(
            key="test_template",
            name="Test Template",
            template_text="Answer this question: {{question}}"
        )
        question = Question(text="What is the capital of France?")
        
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable is not set"):
                generate_output(template, question)
    
    @patch('services.llm.OpenAI')
    def test_generate_outputs(self, mock_openai_class, mock_openai_response):
        """Test generating outputs for multiple templates"""
        # Setup mock
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_openai_response
        mock_openai_class.return_value = mock_client
        
        templates = [
            Template(
                key="template1",
                name="Template 1",
                template_text="Answer: {{question}}"
            ),
            Template(
                key="template2",
                name="Template 2",
                template_text="Please answer: {{question}}"
            )
        ]
        question = Question(text="What is the capital of France?")
        
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            results = generate_outputs(templates, question)
        
        # Verify we got results for both templates
        assert len(results) == 2
        
        # Verify each result is a Generation object
        for i, result in enumerate(results):
            assert isinstance(result, Generation)
            assert result.template_id is None  # Will be set when saved to DB
            assert result.question_id is None  # Will be set when saved to DB
            assert result.output_text == "Mocked response"
            assert result.llm_model == "gpt-4o-mini"
            assert result.latency == 10 / 150
            assert result.output_tokens == 10
            assert result.input_tokens == 20
        
        # Verify OpenAI was called twice (once per template)
        assert mock_client.chat.completions.create.call_count == 2
    
    @patch('services.llm.OpenAI')
    def test_generate_outputs_with_client(self, mock_openai_class, mock_openai_response):
        """Test generating outputs with provided client"""
        # Setup mock
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_openai_response
        
        templates = [
            Template(
                key="template1",
                name="Template 1",
                template_text="Answer: {{question}}"
            )
        ]
        question = Question(text="What is the capital of France?")
        
        results = generate_outputs(templates, question, mock_client)
        
        assert len(results) == 1
        assert isinstance(results[0], Generation)
        assert results[0].output_text == "Mocked response"
        
        # Verify OpenAI class wasn't instantiated since we provided a client
        mock_openai_class.assert_not_called()
    
    def test_generate_outputs_no_api_key(self):
        """Test generating outputs without API key"""
        templates = [
            Template(
                key="template1",
                name="Template 1",
                template_text="Answer: {{question}}"
            )
        ]
        question = Question(text="What is the capital of France?")
        
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable is not set"):
                generate_outputs(templates, question)
