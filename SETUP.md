# Newsletter AI Setup Guide

## ✅ Completed: Project Foundation

The project foundation has been successfully set up with:

- **FastAPI** with proper project structure
- **Pydantic** models for data validation
- **SQLAlchemy** with Neon PostgreSQL support (fallback to SQLite)
- **Portia AI SDK** configured with Google Gemini as primary LLM
- **Upstash Redis** and **Upstash Vector** integration
- **Modern cloud-native architecture**

## 🚀 Quick Start

### 1. Activate Virtual Environment
```bash
source venv/bin/activate
# or
./venv/bin/python [command]
```

### 2. Run the Application
```bash
./venv/bin/python run.py
```

The API will be available at: http://localhost:8000

### 3. View API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔧 Configuration

### Environment Variables
Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

### Required Services

#### 1. Google Gemini API
- Get API key from: https://makersuite.google.com/app/apikey
- Add to `.env`: `GOOGLE_API_KEY=your_key_here`

#### 2. Neon Database (PostgreSQL)
- Sign up at: https://neon.tech
- Create database and get connection string
- Add to `.env`: `DATABASE_URL=postgresql://...`

#### 3. Upstash Redis
- Sign up at: https://upstash.com
- Create Redis database
- Add to `.env`: `UPSTASH_REDIS_URL=rediss://...`

#### 4. Upstash Vector
- Create Vector database at Upstash
- Add to `.env`: `UPSTASH_VECTOR_URL=https://...`

#### 5. External APIs
- **Resend**: Email service - https://resend.com
- **Tavily**: Search API - https://tavily.com

## 🏗️ Architecture

### Tech Stack
- **Backend**: FastAPI + SQLAlchemy + Pydantic
- **Database**: Neon PostgreSQL (with SQLite fallback)
- **Cache**: Upstash Redis
- **Vector DB**: Upstash Vector
- **AI**: Portia AI + Google Gemini
- **Frontend**: Streamlit (upcoming)

### Project Structure
```
app/
├── api/           # FastAPI routes
├── core/          # Configuration and database
├── models/        # SQLAlchemy models
├── schemas/       # Pydantic schemas
├── services/      # Business logic (Upstash, embeddings)
└── portia/        # Portia AI agents
```

## 📋 Next Tasks

1. **Implement core data models** (Task 2)
2. **Create landing page with OTP auth** (Task 3)
3. **Set up Portia AI agents** (Task 4)
4. **Build user preferences system** (Task 5)

## 🔍 Health Check

Test the setup:
```bash
./venv/bin/python -c "from app.main import app; print('✅ Setup successful!')"
```

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Make sure virtual environment is activated
2. **Database Errors**: Expected without Neon setup - uses SQLite fallback
3. **Portia Warnings**: Expected without API keys configured
4. **Missing Dependencies**: Run `pip install -r requirements.txt` in venv

### Development Mode
The app runs with SQLite and mock services by default for development without external dependencies.