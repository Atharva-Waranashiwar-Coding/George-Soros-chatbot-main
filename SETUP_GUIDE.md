# Complete Setup Guide

This guide walks through setting up both the backend and frontend on your local machine.

## Prerequisites

- **Python 3.8+** - [Download](https://www.python.org/downloads/)
- **Node.js 16+ & npm** - [Download](https://nodejs.org/)
- **Git** - [Download](https://git-scm.com/)
- **Google Gemini API Key** - [Get free key](https://makersuite.google.com/app/apikey)
- **A code editor** (VS Code recommended)

## Step 1: Clone the Repository

```bash
git clone <your-repo-url>
cd soros-insights-chatbot
```

## Step 2: Configure Environment Variables

1. **Copy the environment template**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` and add your API key**
   ```bash
   # Open in your editor
   nano .env
   
   # Or on macOS:
   open -a TextEdit .env
   ```

3. **Add your Gemini API key**
   ```
   GEMINI_API_KEY=your_actual_key_here
   ```

## Step 3: Backend Setup

Open a **terminal window 1** and run:

```bash
# Navigate to backend directory
cd soros-backend-main

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start the server
python manage.py runserver
```

**Expected output:**
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

### Verify Backend

In a new terminal, test the API:
```bash
curl -X POST http://127.0.0.1:8000/api/ragbot/ \
  -H "Content-Type: application/json" \
  -d '{"message": "How would Soros think about market reflexivity?"}'
```

## Step 4: Frontend Setup

Open a **terminal window 2** (keep backend running) and run:

```bash
# Navigate to frontend directory
cd soros-ui-main

# Install dependencies
npm install

# Start development server
npm run dev
```

**Expected output:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Press h to show help
```

## Step 5: Access the Application

1. **Open browser** to the URL shown (typically `http://localhost:5173`)
2. **Navigate to Chatbot page**
3. **Send a test message** like: *"How would Soros view market cycles?"*

## Troubleshooting

### "Gemini API Key Missing" Error

**Problem:** Backend shows "API key not configured"

**Solution:**
```bash
# Make sure .env file exists in backend root
ls -la .env

# Verify the key is set
cat .env | grep GEMINI_API_KEY

# If not set, edit the file
nano .env  # Add: GEMINI_API_KEY=your_key

# Restart the server
python manage.py runserver
```

### Frontend Can't Reach Backend

**Problem:** CORS error or connection refused

**Solution:**
1. Verify backend is running: `http://127.0.0.1:8000/`
2. Check browser console (F12) for errors
3. Restart frontend: `npm run dev`

### Port Already in Use

**Problem:** "Address already in use" error

**Solution:**
```bash
# Find what's using the port (Backend uses 8000)
lsof -i :8000
# Kill the process
kill -9 <PID>

# Or use different port
python manage.py runserver 8001

# For frontend (uses 5173)
lsof -i :5173
kill -9 <PID>
```

### Python Version Issues

**Problem:** "python3: command not found"

**Solution:**
```bash
# Check installed Python versions
python --version
python3 --version

# Use whichever is 3.8+
python3 -m venv .venv  # Or just python
```

### Chroma Database Issues

**Problem:** "Knowledge base not found" error

**Solution:**
```bash
# Check if chroma_db exists
ls -la soros-backend-main/chroma_db/

# If missing, the knowledge base needs to be initialized
# This happens automatically, but ensure permissions are correct
chmod -R 755 soros-backend-main/chroma_db/
```

## Running Tests

### Backend Tests

```bash
cd soros-backend-main
python manage.py test financials_api
```

**Run specific test:**
```bash
python manage.py test financials_api.tests.RAGViewTestCase.test_rag_valid_question
```

**Run with verbose output:**
```bash
python manage.py test -v 2 financials_api
```

### Frontend Tests (if configured)

```bash
cd soros-ui-main
npm test
```

## Development Workflow

### Making Backend Changes

1. Edit files in `soros-backend-main/`
2. Django reloads automatically (most changes)
3. If you modify models: `python manage.py makemigrations && python manage.py migrate`
4. Check `http://127.0.0.1:8000/api/ragbot/` for API changes

### Making Frontend Changes

1. Edit files in `soros-ui-main/src/`
2. Vite hot-reloads automatically
3. Check `http://localhost:5173/` (refreshes live)

### Adding Dependencies

**Backend:**
```bash
cd soros-backend-main
pip install new-package
pip freeze > requirements.txt  # Update requirements file
```

**Frontend:**
```bash
cd soros-ui-main
npm install new-package
# package.json updates automatically
```

## Common Commands Reference

### Backend

```bash
# Activate venv
source soros-backend-main/.venv/bin/activate

# Run server
python manage.py runserver

# Run migrations
python manage.py migrate

# Create superuser (if needed)
python manage.py createsuperuser

# Access Django shell
python manage.py shell

# Run tests
python manage.py test

# Collect static files
python manage.py collectstatic
```

### Frontend

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint

# Format code (if prettier configured)
npm run format
```

## Production Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed production deployment instructions.

## Project Structure Reference

```
├── README.md              # Main project documentation
├── SETUP_GUIDE.md        # This file
├── DEPLOYMENT.md         # Production deployment guide
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore patterns
│
├── soros-backend-main/
│   ├── manage.py
│   ├── requirements.txt
│   ├── soros_backend/    # Django project settings
│   └── financials_api/   # Main Django app
│       ├── views/        # API endpoints
│       ├── tests.py      # Test suite
│       └── ...
│
└── soros-ui-main/
    ├── package.json
    ├── src/
    │   ├── pages/        # React pages
    │   ├── components/   # Reusable components
    │   ├── services/     # API integration
    │   └── ...
    └── ...
```

## Getting Help

1. **Check error messages** - Django and console errors usually point to solutions
2. **Read the API docs** - See [README.md](./README.md) for API documentation
3. **Check logs** - Backend: terminal output | Frontend: browser console (F12)
4. **Review code comments** - Check relevant source files for inline documentation
5. **Google the error** - Most Django/Node errors are well documented

## Next Steps

After successful setup:

1. ✅ Verify both frontend and backend are running
2. ✅ Send a test message through the chatbot
3. ✅ Run the test suite
4. ✅ Explore the codebase
5. ✅ Read [DEPLOYMENT.md](./DEPLOYMENT.md) for production setup

---

**Happy coding!** 🚀
