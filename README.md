# RAG Chatbot: George Soros Insights

A React and Django application that retrieves relevant Q&A context from ChromaDB before generating educational answers with Google Gemini. It also includes market-data and pair-analysis views.

**Stack:** Python, Django REST Framework, React, Vite, ChromaDB, Google Gemini, yfinance.

## Local demo

Start the backend and frontend using the [Quick Start](#-quick-start) below. Open the Chatbot page and ask: **How does reflexivity affect market prices?** The retrieval layer indexes the checked-in Q&A spreadsheet and supplies relevant entries to answer generation.

No hosted demo is currently linked. This is an educational application; generated responses and market analysis require independent review.

## Architecture notes

- Retrieval and generation live in separate modules, so embedding and answer-generation choices can evolve independently.
- Chroma stores a persistent Q&A index and initializes it when the collection is empty. The default embedding function has an optional sentence-transformer path.
- Django serves the API; React handles chat and market-analysis views. Local Django settings require hardening before a public deployment.

<details>
<summary>Setup, API reference, and development details</summary>

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** (for backend)
- **Node.js 16+** & **npm** (for frontend)
- **Google Gemini API Key** (get it from [Google AI Studio](https://makersuite.google.com/app/apikey))
- **Git**

### Setup Backend

1. **Navigate to backend directory**
   ```bash
   cd soros-backend-main
   ```

2. **Create and activate Python virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp ../.env.example .env
   # Edit .env and add your Google Gemini API key
   export GEMINI_API_KEY="your_key_here"
   # or
   export GOOGLE_API_KEY="your_key_here"
   ```

5. **Run migrations**
   ```bash
   export DJANGO_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(50))')"
   python manage.py migrate
   ```

6. **Start the backend server**
   ```bash
   python manage.py runserver
   ```
   Backend will be available at `http://127.0.0.1:8000`

### Setup Frontend

1. **In a new terminal, navigate to frontend directory**
   ```bash
   cd soros-ui-main
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```
   Frontend will be available at `http://localhost:5173` (or shown in terminal)

### Verify Setup

- Open your browser to the frontend URL
- Navigate to the Chatbot page
- Send a test message like: *"How would Soros think about market reflexivity?"*
- You should receive an AI-generated response

## 🔑 Environment Variables

Copy `.env.example` to `.env` in the backend directory:

```bash
# Google Generative AI Configuration
GEMINI_API_KEY=your_api_key_here
DJANGO_SECRET_KEY=your_unique_random_signing_secret

# Django Configuration (optional)
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:3000
```

## 📖 API Documentation

### RAG Chatbot Endpoint

**Endpoint:** `POST /api/ragbot/`

**Request:**
```json
{
  "message": "How would Soros think about market psychology in tech stocks?"
}
```

**Response:**
```json
{
  "reply": "George Soros believed that markets are driven by... [educational response based on RAG knowledge base]"
}
```

**Error Responses:**
- `400 Bad Request`: Missing `message` field
- `401 Unauthorized`: Missing or invalid Gemini API key
- `500 Internal Server Error`: Knowledge base not found or API failure

### Pair Trading Endpoint

**Endpoint:** `POST /api/pairs/`

**Request:**
```json
{
  "ticker1": "STOCK1",
  "ticker2": "STOCK2",
  "lookback": 252
}
```

**Response:**
```json
{
  "correlation": 0.75,
  "current_spread": -2.5,
  "mean_spread": 0,
  "std_spread": 1.8
}
```

## 🧪 Testing

### Run Backend Tests

```bash
cd soros-backend-main
python manage.py test financials_api
```

### Run Specific RAG Chatbot Tests

```bash
python manage.py test financials_api.tests.RAGViewTestCase
```

### Run Frontend Tests

```bash
cd soros-ui-main
npm run test
```

## 📋 Features

### RAG Chatbot
- **Knowledge Base**: Curated insights from George Soros's published works
- **Smart Retrieval**: Chroma vector database for semantic search
- **AI Generation**: Google Gemini API for contextual responses
- **Educational Focus**: System instructions ensure only educational, philosophical content (no financial advice)
- **Ticker Awareness**: Can reference specific stocks in educational context

### Pair Trading Analysis
- **Statistical Analysis**: Cointegration and correlation analysis
- **Real-time Data**: Yahoo Finance integration
- **Spread Analysis**: Mean-reversion opportunity detection

## 🔒 Security Notes

1. **Never commit API keys**: Keep `.env` out of version control
2. **API Key Validation**: Missing keys are caught and reported clearly
3. **Rate Limiting**: Implement rate limiting for production deployments
4. **CORS**: Configure CORS properly for your domain
5. **Input Validation**: All API inputs are validated server-side

## 🚀 Deployment

For production deployment instructions, see [DEPLOYMENT.md](./DEPLOYMENT.md)

### Quick Production Checklist

- [ ] Set `DEBUG=False` in settings.py
- [ ] Configure `SECRET_KEY` with a strong random value
- [ ] Set up HTTPS/SSL certificate
- [ ] Configure proper `ALLOWED_HOSTS`
- [ ] Set `CORS_ALLOWED_ORIGINS` to your frontend domain
- [ ] Use environment variables for all sensitive config
- [ ] Run `python manage.py collectstatic` for static files
- [ ] Consider using Gunicorn/uWSGI with Nginx
- [ ] Monitor error logs and API performance

## 📚 Knowledge Base

The RAG chatbot draws from these sources:
- George Soros's "The Alchemy of Finance"
- Market reflexivity principles
- Soros's public speeches and writings
- Historical market analysis case studies

Located in: `soros-backend-main/chroma_db/`

## 🛠️ Troubleshooting

### "Gemini API Key Missing" Error
- Ensure you've created a `.env` file or set environment variables
- Get a free key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- Restart the backend server after adding the key

### "Knowledge Base Not Found" Error
- Ensure `chroma_db/` directory exists
- Check that vector embeddings were properly initialized

### Frontend Can't Connect to Backend
- Check that backend is running on `http://127.0.0.1:8000`
- Check browser console for CORS errors
- Verify `CORS_ALLOWED_ORIGINS` in backend settings

### Port Already in Use
- Backend: `lsof -i :8000` and `kill -9 <PID>`
- Frontend: `lsof -i :5173` and `kill -9 <PID>`

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Run tests: `npm run test` (frontend), `python manage.py test` (backend)
4. Commit: `git commit -am 'Add your feature'`
5. Push: `git push origin feature/your-feature`
6. Open a Pull Request

## 📄 License

This project is for educational purposes.

## 👨‍💼 About

Built as an educational tool to explore George Soros's investment philosophy and market reflexivity principles through conversational AI.

</details>
