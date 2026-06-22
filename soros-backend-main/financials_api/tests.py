import json
import os
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status


class RAGViewTestCase(TestCase):
    """
    Comprehensive test suite for the RAG chatbot API endpoint.
    Tests various scenarios including success, missing API keys, invalid inputs, and error handling.
    """

    def setUp(self):
        """Set up test client and base URL."""
        self.client = Client()
        self.url = reverse('ragbot')  # Adjust if your URL name differs
        # Alternative: self.url = '/api/ragbot/'

    def test_rag_endpoint_exists(self):
        """Test that the RAG endpoint is accessible."""
        response = self.client.post(self.url)
        # Should get 400 Bad Request (missing message), not 404
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ==================== Valid Request Tests ====================

    @patch('financials_api.interface._chatbot')
    def test_rag_valid_question(self, mock_chatbot):
        """Test RAG endpoint with a valid question."""
        # Mock successful chatbot response
        mock_chatbot.answer.return_value = "Soros would focus on reflexivity in this market."
        
        payload = {"message": "How would Soros think about this market?"}
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('reply', data)
        self.assertIn('Soros', data['reply'])

    @patch('financials_api.interface._chatbot')
    def test_rag_single_word_question(self, mock_chatbot):
        """Test RAG endpoint with a single-word question."""
        mock_chatbot.answer.return_value = "Reflexivity is the key concept."
        
        payload = {"message": "Reflexivity?"}
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('reply', data)

    @patch('financials_api.interface._chatbot')
    def test_rag_complex_question(self, mock_chatbot):
        """Test RAG endpoint with a complex, multi-sentence question."""
        mock_chatbot.answer.return_value = "This is a complex analysis..."
        
        payload = {
            "message": "Given the current market conditions, with tech stocks rising, interest rates falling, "
                       "and geopolitical tensions increasing, how would Soros analyze this reflexive cycle?"
        }
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('reply', data)

    @patch('financials_api.interface._chatbot')
    def test_rag_ticker_mention(self, mock_chatbot):
        """Test RAG endpoint with a ticker symbol in the question."""
        mock_chatbot.answer.return_value = "Regarding Tesla in the context of Soros's philosophy..."
        
        payload = {"message": "What would Soros think about TSLA?"}
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('reply', data)

    @patch('financials_api.interface._chatbot')
    def test_rag_response_format(self, mock_chatbot):
        """Test that RAG response has correct JSON structure."""
        mock_chatbot.answer.return_value = "Sample response"
        
        payload = {"message": "Test question"}
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        # Should have 'reply' key at minimum
        self.assertIn('reply', data)
        self.assertIsInstance(data['reply'], str)

    # ==================== Invalid Input Tests ====================

    def test_rag_missing_message_field(self):
        """Test RAG endpoint without 'message' field."""
        payload = {"question": "This is wrong field"}
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertIn('error', data)
        self.assertIn('Missing required field', data['error'])

    def test_rag_empty_message(self):
        """Test RAG endpoint with empty message string."""
        payload = {"message": ""}
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertIn('error', data)

    def test_rag_whitespace_only_message(self):
        """Test RAG endpoint with whitespace-only message."""
        payload = {"message": "   \n  \t  "}
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertIn('error', data)

    def test_rag_null_message(self):
        """Test RAG endpoint with null message value."""
        payload = {"message": None}
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertIn('error', data)

    def test_rag_missing_json_body(self):
        """Test RAG endpoint with missing JSON body."""
        response = self.client.post(
            self.url,
            data='',
            content_type='application/json'
        )
        
        # Should be 400, not 500
        self.assertIn(
            response.status_code,
            [status.HTTP_400_BAD_REQUEST, status.HTTP_500_INTERNAL_SERVER_ERROR]
        )

    # ==================== API Key & Authorization Tests ====================

    @patch('financials_api.interface._chatbot', None)
    @patch('financials_api.interface._chatbot_error', "Gemini API key not configured")
    def test_rag_missing_api_key(self):
        """Test RAG endpoint returns 401 when Gemini API key is missing."""
        with patch('financials_api.interface._chatbot_error', "Gemini API key not configured"):
            payload = {"message": "Test question"}
            response = self.client.post(
                self.url,
                data=json.dumps(payload),
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            data = response.json()
            self.assertIn('error', data)
            self.assertIn('Missing Gemini API Key', data['error'])
            self.assertIn('reply', data)

    @patch('financials_api.interface._chatbot', None)
    def test_rag_initialization_error_not_api_key(self):
        """Test RAG endpoint returns 500 for non-API-key initialization errors."""
        with patch('financials_api.interface._chatbot_error', "Chroma database not found"):
            payload = {"message": "Test question"}
            response = self.client.post(
                self.url,
                data=json.dumps(payload),
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            data = response.json()
            self.assertIn('error', data)

    # ==================== Error Handling Tests ====================

    @patch('financials_api.interface._chatbot')
    def test_rag_knowledge_base_not_found(self, mock_chatbot):
        """Test RAG endpoint when knowledge base file is missing."""
        mock_chatbot.answer.side_effect = FileNotFoundError("Chroma database not found")
        
        payload = {"message": "Test question"}
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        data = response.json()
        self.assertIn('error', data)
        self.assertIn('Knowledge base', data['error'])

    @patch('financials_api.interface._chatbot')
    def test_rag_runtime_error(self, mock_chatbot):
        """Test RAG endpoint when a runtime error occurs."""
        mock_chatbot.answer.side_effect = RuntimeError("API rate limit exceeded")
        
        payload = {"message": "Test question"}
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        data = response.json()
        self.assertIn('error', data)

    @patch('financials_api.interface._chatbot')
    def test_rag_generic_exception(self, mock_chatbot):
        """Test RAG endpoint handles unexpected exceptions."""
        mock_chatbot.answer.side_effect = Exception("Unexpected error")
        
        payload = {"message": "Test question"}
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        data = response.json()
        self.assertIn('error', data)
        self.assertIn('reply', data)

    @patch('financials_api.interface._chatbot')
    def test_rag_answer_error_in_result(self, mock_chatbot):
        """Test when chatbot returns error message in answer."""
        mock_chatbot.answer.return_value = "Error: Something went wrong"
        
        payload = {"message": "Test question"}
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Should return 500 since answer contains error
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    # ==================== HTTP Method Tests ====================

    def test_rag_get_not_allowed(self):
        """Test that GET requests are not allowed."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_rag_put_not_allowed(self):
        """Test that PUT requests are not allowed."""
        payload = {"message": "Test"}
        response = self.client.put(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_rag_delete_not_allowed(self):
        """Test that DELETE requests are not allowed."""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # ==================== Content Type Tests ====================

    @patch('financials_api.interface._chatbot')
    def test_rag_form_data_content_type(self, mock_chatbot):
        """Test RAG endpoint with form data content type."""
        mock_chatbot.answer.return_value = "Sample response"
        
        response = self.client.post(
            self.url,
            data={"message": "Test question"},
        )
        
        # May be successful depending on framework configuration
        self.assertIn(
            response.status_code,
            [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]
        )

    # ==================== Response Content Tests ====================

    @patch('financials_api.interface._chatbot')
    def test_rag_response_not_empty(self, mock_chatbot):
        """Test that RAG response is not empty."""
        mock_chatbot.answer.return_value = "Valid response"
        
        payload = {"message": "Test"}
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        data = response.json()
        self.assertGreater(len(data['reply']), 0)

    @patch('financials_api.interface._chatbot')
    def test_rag_response_is_string(self, mock_chatbot):
        """Test that RAG reply is a string."""
        mock_chatbot.answer.return_value = "Test"
        
        payload = {"message": "Test"}
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        data = response.json()
        self.assertIsInstance(data['reply'], str)

    # ==================== Large Input Tests ====================

    @patch('financials_api.interface._chatbot')
    def test_rag_very_long_message(self, mock_chatbot):
        """Test RAG endpoint with very long message."""
        mock_chatbot.answer.return_value = "Long message response"
        
        long_message = "test " * 1000  # ~5000 characters
        payload = {"message": long_message}
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Should succeed or have proper error
        self.assertIn(
            response.status_code,
            [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE]
        )


class RAGInterfaceTestCase(TestCase):
    """
    Unit tests for the RAG interface module.
    Tests the answer_question function and SorosRAGChatbot class.
    """

    @patch('financials_api.interface._chatbot')
    def test_answer_question_success(self, mock_chatbot):
        """Test answer_question function with successful chatbot."""
        from financials_api.interface import answer_question
        
        mock_chatbot.answer.return_value = "Test answer"
        result = answer_question("Test question")
        
        self.assertIn('answer', result)
        self.assertEqual(result['answer'], "Test answer")

    def test_answer_question_no_chatbot(self):
        """Test answer_question function when chatbot is not initialized."""
        from financials_api.interface import answer_question
        
        with patch('financials_api.interface._chatbot', None):
            with patch('financials_api.interface._chatbot_error', "Test error"):
                result = answer_question("Test question")
                
                self.assertIn('answer', result)
                self.assertIn('Error', result['answer'])

    def test_answer_question_api_key_error(self):
        """Test answer_question handles API key errors."""
        from financials_api.interface import answer_question
        
        with patch('financials_api.interface._chatbot', None):
            with patch('financials_api.interface._chatbot_error', "Gemini API key not configured"):
                result = answer_question("Test question")
                
                self.assertIn('answer', result)
                self.assertIn('API key', result['answer'])
                self.assertIn('makersuite.google.com', result['answer'])

