# 🚀 Newsletter AI - Deployment Guide

This guide covers multiple deployment options for your Newsletter AI system, from simple single-service deployments to full production setups.

## 📋 Deployment Architecture

Your Newsletter AI has **two main components**:
- **FastAPI Backend** (Port 8000): API server with Portia AI agents
- **Streamlit Frontend** (Port 8501): User interface and dashboard

## 🎯 Quick Deployment Options

### **Option 1: Render.com (Recommended for Production)**

#### **✅ Pros:**
- Free tier available for both services
- Automatic SSL certificates
- Git-based deployments
- Managed PostgreSQL database
- Zero configuration scaling

#### **📋 Setup Steps:**

1. **Fork/Clone your repository to GitHub**

2. **Deploy Backend Service:**
   - Go to [Render Dashboard](https://render.com)
   - Click "New" → "Web Service"
   - Connect your GitHub repo
   - Use these settings:
     ```
     Name: newsletter-ai-backend
     Runtime: Python 3
     Build Command: pip install -r requirements.txt
     Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```

3. **Deploy Frontend Service:**
   - Create another Web Service
   - Use these settings:
     ```
     Name: newsletter-ai-frontend  
     Runtime: Python 3
     Build Command: pip install -r requirements.txt
     Start Command: streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0
     ```

4. **Add Environment Variables:**
   ```env
   # Backend Service
   DATABASE_URL=<your-render-postgres-url>
   GOOGLE_API_KEY=<your-gemini-key>
   PORTIA_API_KEY=<your-portia-key>
   RESEND_API_KEY=<your-resend-key>
   TAVILY_API_KEY=<your-tavily-key>
   UPSTASH_REDIS_REST_URL=<your-upstash-redis-url>
   UPSTASH_REDIS_REST_TOKEN=<your-upstash-redis-token>
   UPSTASH_VECTOR_URL=<your-upstash-vector-url>
   UPSTASH_VECTOR_TOKEN=<your-upstash-vector-token>
   SECRET_KEY=<your-secret-key>

   # Frontend Service  
   API_BASE_URL=https://newsletter-ai-backend.onrender.com/api/v1
   ```

5. **Create PostgreSQL Database:**
   - In Render Dashboard: "New" → "PostgreSQL"
   - Connect it to your backend service

---

### **Option 2: Railway.app**

#### **✅ Pros:**
- Excellent developer experience
- Automatic deployments from Git
- Built-in monitoring and logs
- Simple pricing model

#### **📋 Setup Steps:**

1. **Deploy with Railway:**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login and deploy
   railway login
   railway init
   railway up
   ```

2. **Configure Services:**
   - Backend: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Frontend: `streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0`

---

### **Option 3: Docker Deployment (Any Cloud Provider)**

#### **✅ Pros:**
- Works on any cloud platform
- Consistent environment
- Easy local development
- Container orchestration ready

#### **📋 Local Development:**
```bash
# Start all services with Docker Compose
docker-compose up -d

# Access services:
# Frontend: http://localhost:8501
# Backend: http://localhost:8000
# Database: localhost:5432
```

#### **📋 Production Deployment:**

**Google Cloud Run:**
```bash
# Build and deploy backend
gcloud run deploy newsletter-ai-backend \
  --source . \
  --port 8000 \
  --allow-unauthenticated

# Build and deploy frontend  
gcloud run deploy newsletter-ai-frontend \
  --source . \
  --port 8501 \
  --set-env-vars API_BASE_URL=<backend-url>/api/v1
```

**AWS ECS/Fargate:**
```bash
# Build and push to ECR
aws ecr create-repository --repository-name newsletter-ai
docker build -t newsletter-ai .
docker tag newsletter-ai:latest <aws-account>.dkr.ecr.us-east-1.amazonaws.com/newsletter-ai:latest
docker push <aws-account>.dkr.ecr.us-east-1.amazonaws.com/newsletter-ai:latest

# Deploy with ECS service definitions (backend + frontend)
```

---

### **Option 4: Streamlit Community Cloud (Frontend Only)**

#### **⚠️ Limitations:**
- Can only host the Streamlit frontend
- Backend must be deployed separately
- Not recommended for production

#### **📋 Setup:**
1. Deploy backend on Render/Railway
2. Deploy frontend on [Streamlit Cloud](https://streamlit.io/cloud)
3. Set `API_BASE_URL` environment variable

---

## 🔧 Configuration Guide

### **Environment Variables Setup**

Create these environment variables in your deployment platform:

```env
# Core AI Services (Required)
GOOGLE_API_KEY=your_google_gemini_key
PORTIA_API_KEY=your_portia_key
OPENAI_API_KEY=your_openai_key  # Fallback

# External Services (Required)
RESEND_API_KEY=your_resend_key
TAVILY_API_KEY=your_tavily_key

# Cloud Storage (Required for production)
UPSTASH_REDIS_REST_URL=your_redis_url
UPSTASH_REDIS_REST_TOKEN=your_redis_token
UPSTASH_VECTOR_URL=your_vector_url
UPSTASH_VECTOR_TOKEN=your_vector_token

# Database (Platform-specific)
DATABASE_URL=postgresql://user:pass@host:port/db

# Security (Required)
SECRET_KEY=your-secret-key-minimum-32-characters

# Frontend Configuration
API_BASE_URL=https://your-backend-url.com/api/v1
```

### **Database Setup**

**For Render/Railway:**
- Use their managed PostgreSQL service
- Copy the connection string to `DATABASE_URL`

**For Docker:**
- PostgreSQL container included in docker-compose.yml
- Uses local volumes for persistence

**For Production:**
- Recommended: Neon, Supabase, or managed PostgreSQL
- Ensure timezone support: `SET TIME ZONE 'UTC'`

---

## 📊 Service Dependencies

### **Required External Services:**

1. **Upstash Redis** (Cache & Memory)
   - Sign up: [upstash.com](https://upstash.com)
   - Create Redis database
   - Copy REST URL and token

2. **Upstash Vector** (RAG System) 
   - Create Vector database
   - Use Google Gemini text-embedding-004 model
   - Copy URL and token

3. **Google AI Studio** (Primary LLM)
   - Get API key: [aistudio.google.com](https://aistudio.google.com)

4. **Portia AI** (Agent Framework)
   - Get API key from Portia AI platform

5. **Resend** (Email Delivery)
   - Sign up: [resend.com](https://resend.com)
   - Verify your domain

6. **Tavily** (Web Search)
   - Get API key: [tavily.com](https://tavily.com)

---

## 🚀 Recommended Deployment Flow

### **For Development:**
```bash
# 1. Local development with Docker
docker-compose up -d

# 2. Test all endpoints
curl http://localhost:8000/health
curl http://localhost:8501
```

### **For Production:**
```bash
# 1. Deploy to Render.com (easiest)
# - Use render.yaml configuration
# - Set environment variables
# - Connect PostgreSQL database

# 2. Configure external services
# - Upstash Redis & Vector
# - Google AI Studio
# - Resend email

# 3. Test production deployment
curl https://your-backend.onrender.com/health
```

---

## 🔍 Monitoring & Troubleshooting

### **Health Check Endpoints:**
- Backend: `GET /health`
- API Docs: `GET /docs`
- Monitoring: `GET /api/v1/newsletters/monitoring/dashboard`

### **Common Issues:**

1. **Frontend can't connect to backend:**
   - Check `API_BASE_URL` environment variable
   - Ensure backend is deployed and healthy

2. **Database connection errors:**
   - Verify `DATABASE_URL` format
   - Check database service status

3. **Email delivery failures:**
   - Verify `RESEND_API_KEY`
   - Check domain verification

4. **AI agent errors:**
   - Verify all API keys (Google, Portia, OpenAI)
   - Check external service quotas

---

## 💰 Cost Estimates

### **Free Tier Capabilities:**
- **Render.com**: 750 hours/month (backend + frontend)
- **Upstash**: 10K requests/day (Redis + Vector)
- **Google AI**: $0.15/1M tokens (Gemini)
- **Resend**: 3K emails/month
- **Total**: ~$0-20/month for moderate usage

### **Production Scale:**
- **Render Pro**: $7/service/month
- **Database**: $7/month (managed PostgreSQL)
- **External APIs**: $10-50/month (depending on usage)
- **Total**: ~$30-80/month for production usage

---

## 🎯 Quick Start Commands

**Deploy to Render (fastest):**
```bash
# 1. Push code to GitHub
git add . && git commit -m "Deploy to Render" && git push

# 2. Import in Render dashboard
# 3. Set environment variables
# 4. Deploy!
```

**Deploy with Docker:**
```bash
# Local development
docker-compose up -d

# Production build
docker build -t newsletter-ai .
docker run -p 8000:8000 -p 8501:8501 newsletter-ai
```

**Test deployment:**
```bash
# Health check
curl https://your-backend-url.com/health

# Generate newsletter
curl -X POST https://your-backend-url.com/api/v1/newsletters/generate \
  -H "Content-Type: application/json" \
  -d '{"send_immediately": false}'
```

---

Choose the deployment option that best fits your needs. **Render.com is recommended** for most users due to its simplicity and generous free tier!