
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..interface import answer_question as answer_question_rag, _chatbot, _chatbot_error


class RAGView(APIView):
    """
    Handles chatbot requests using the Chroma + Gemini RAG pipeline.
    
    POST /api/ragbot/
    Request: { "message": "Your question here" }
    Response: { "reply": "Generated answer from RAG pipeline" }
    
    Error Responses:
    - 400: Missing or empty message
    - 401: Gemini API key is not configured
    - 500: Knowledge base not found or other processing errors
    """
    
    def post(self, request):
        # Validate request
        query = request.data.get('message', None)
        if not query:
            return Response(
                {
                    "error": "Missing required field",
                    "details": "No query (message) provided.",
                    "reply": "No query (message) provided."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        query = query.strip() if isinstance(query, str) else str(query)
        if not query:
            return Response(
                {
                    "error": "Empty message",
                    "details": "The message field cannot be empty.",
                    "reply": "The message field cannot be empty."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if chatbot was initialized successfully
        if _chatbot is None:
            # Check if it's due to missing API key
            if "API key" in str(_chatbot_error).lower() or "gemini" in str(_chatbot_error).lower():
                return Response(
                    {
                        "error": "Missing Gemini API Key",
                        "details": "GEMINI_API_KEY or GOOGLE_API_KEY environment variable is not set. "
                                   "Please configure your API key at https://makersuite.google.com/app/apikey",
                        "reply": "Error: Gemini API key is not configured. Please contact the administrator."
                    },
                    status=status.HTTP_401_UNAUTHORIZED
                )
            else:
                return Response(
                    {
                        "error": "RAG pipeline initialization failed",
                        "details": _chatbot_error,
                        "reply": f"Error: RAG pipeline not available ({_chatbot_error})."
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        # Process the query
        try:
            result = answer_question_rag(query)
            
            # Check if the result contains an error message
            answer = result.get("answer", "Could not generate answer from knowledge base.")
            if "Error:" in answer:
                # If it's an API key error, return 401
                if "API key" in answer.lower():
                    return Response(
                        {
                            "error": "Missing Gemini API Key",
                            "details": answer,
                            "reply": answer
                        },
                        status=status.HTTP_401_UNAUTHORIZED
                    )
                # Other errors are 500s
                return Response(
                    {"error": "Processing error", "details": answer, "reply": answer},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            return Response(
                {"reply": answer},
                status=status.HTTP_200_OK
            )
        
        except FileNotFoundError as e:
            print(f"Error: RAG knowledge base not found: {e}")
            return Response(
                {
                    "error": "Knowledge base not found",
                    "details": "The RAG knowledge base (Chroma database) could not be found.",
                    "reply": "Error: RAG knowledge base not found. Please ensure the database is initialized."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        except RuntimeError as e:
            error_msg = str(e)
            print(f"Error in RAGView: {error_msg}")
            
            # Check if it's an API key error
            if "API key" in error_msg.lower() or "gemini" in error_msg.lower():
                return Response(
                    {
                        "error": "Missing Gemini API Key",
                        "details": error_msg,
                        "reply": "Error: Gemini API key is not configured. Please contact the administrator."
                    },
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            return Response(
                {"error": "Runtime error", "details": error_msg, "reply": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        except Exception as e:
            error_msg = str(e)
            print(f"Error in RAGView: {error_msg}")
            return Response(
                {
                    "error": "Internal server error",
                    "details": error_msg if os.getenv("DEBUG", "False").lower() == "true" else "An unexpected error occurred.",
                    "reply": "An error occurred processing the RAG request."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# SAMPLE Qs

# {"message": "How do you determine if a stock is undervalued?"}
# {"message": "What is intrinsic value?"}
