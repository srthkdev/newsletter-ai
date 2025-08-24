# 🤖 Newsletter AI - Powered by Portia AI

> **A Revolutionary AI-Powered Newsletter Generation System**  
> *Built for the Portia AI Hackathon*

![Portia AI Newsletter System](https://img.shields.io/badge/Powered%20by-Portia%20AI-blue?style=for-the-badge&logo=ai) 
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python)

## 🏆 Hackathon Project Overview

This Newsletter AI system showcases the power of **Portia AI's agent framework** by creating a fully autonomous newsletter generation pipeline. Built for the Portia AI Hackathon, this project demonstrates how multiple AI agents can work together to research, curate, write, and deliver personalized newsletters with minimal human intervention.

<img width="970" height="541" alt="Screenshot 2025-08-24 at 6 09 05 PM" src="https://github.com/user-attachments/assets/f1085db7-8fac-43f9-9615-e26d15308f32" />
<img width="1255" height="718" alt="Screenshot 2025-08-24 at 6 08 48 PM" src="https://github.com/user-achments/assets/32c1a285-b9d1-4f54-91e0-c19b2c6ad75a" />
<img width="1255" height="718" alt="Screenshot 2025-08-24 at 6 08 40 PM" src="https://github.com/user-attachments/assets/3313d7e7-fe07-4473-ace4-c3cb24be61d5" />
<img width="980" height="524" alt="Screenshot 2025-08-24 at 6 07 28 PM" src="https://github.com/user-attachments/assets/dfd25645-982f-4b46-880c-59224b51e337" />
<img width="595" height="521" alt="Screenshot 2025-08-24 at 6 07 10 PM" src="https://github.com/user-attachments/assets/f74ce450-f63b-4ee1-bd12-81c47224ed71" />


### 🎯 Why Portia AI?

**Portia AI** enables us to create sophisticated multi-agent workflows that handle complex tasks like newsletter generation. Our system uses Portia's framework to orchestrate:

- **Research Agents** that discover trending content
- **Writing Agents** that craft engaging narratives  
- **Preference Agents** that learn user behavior
- **Custom Prompt Agents** that interpret natural language requests

## ✨ Features & Capabilities

### 🤖 Multi-Agent AI System (Powered by Portia AI)

#### 1. **Research Agent** 🔍
- **Technology**: Portia AI + Tavily API
- **Function**: Discovers trending content across the web
- **Intelligence**: Filters content by relevance, recency, and quality
- **Data Sources**: 10,000+ news sources, blogs, and publications
- **Status**: ✅ **Fully Operational** with fallback mechanisms

#### 2. **Writing Agent** ✍️
- **Technology**: Portia AI + Google Gemini 2.5-flash
- **Function**: Crafts newsletter content with perfect tone and structure
- **Features**: 
  - Blog-style HTML templates with responsive design
  - AI-generated bullet point summaries (5-6 insights per newsletter)
  - Personalized introductions and conclusions
  - RAG-enhanced content generation
- **Status**: ✅ **Fully Operational** - generates meaningful insights instead of article links

#### 3. **Preference Agent** 🎯
- **Technology**: Portia AI + Redis Memory System
- **Function**: Learns user preferences and behavior patterns
- **Capabilities**:
  - Topic interest tracking
  - Engagement pattern analysis
  - Automatic preference updates
  - Recommendation generation
- **Status**: ✅ **Fully Operational** with enhanced memory storage

#### 4. **Custom Prompt Agent** 💭
- **Technology**: Portia AI + Natural Language Processing
- **Function**: Interprets custom user requests in natural language
- **Features**:
  - Prompt enhancement and optimization
  - Context-aware interpretation
  - Multi-intent understanding
- **Status**: ✅ **Fully Operational**

#### 5. **Mindmap Agent** 🗺️
- **Technology**: Portia AI + Mermaid.js
- **Function**: Creates visual knowledge maps of newsletter content
- **Features**:
  - Interactive zoom/pan controls
  - SVG export and email attachment
  - Keyword extraction and clustering
  - Visual content overview
- **Status**: ✅ **Fully Operational** with robust fallback generation

### 🧠 RAG-Powered Personalization

Our **Retrieval-Augmented Generation (RAG)** system uses:
- **Vector Database**: Upstash Vector with Google Gemini text-embedding-004
- **Semantic Search**: User-scoped content similarity matching
- **Preference Learning**: Automatic preference updates from user behavior
- **Context Enhancement**: Newsletter content enhanced with user history
- **Status**: ✅ **Fully Operational** with Gemini embeddings

### 🎨 Modern Frontend (Streamlit)

#### 📱 Responsive Multi-Page Application
- **Landing Page**: Hero section with OTP authentication
- **Preferences Dashboard**: Interactive topic/tone selection
- **Custom Newsletter Creator**: Natural language prompt interface
- **Newsletter Detail View**: Full content display with mindmap visualization
- **Analytics Page**: Personal insights and performance metrics
- **Monitoring Dashboard**: Real-time agent health tracking

#### 🌟 UI Features
- Modern CSS with gradients and animations
- Mobile-responsive design with proper contrast (#1a202c text on light backgrounds)
- Interactive rating system (1-5 stars)
- Progress tracking and real-time validation
- Mindmap viewer with zoom controls and SVG download
- **Status**: ✅ **Fully Operational** with visibility fixes

### 🚀 Backend Architecture (FastAPI)

#### 📊 Database Models
- **PostgreSQL** with SQLAlchemy ORM
- **User Management**: JWT authentication with OTP verification
- **Newsletter History**: Complete generation tracking with mindmap data
- **Rating System**: User feedback and learning integration
- **Engagement Metrics**: Open rates, clicks, reading patterns
- **Status**: ✅ **Fully Operational** with timezone-aware datetime handling

#### 🔄 Background Processing
- **Newsletter Scheduler**: Automated frequency-based generation
- **Email Delivery**: Resend API integration with retry mechanisms
- **Slack Delivery**: Slack API integration for team communication
- **Error Recovery**: Automatic agent recovery mechanisms
- **Performance Monitoring**: Real-time health tracking
- **Status**: ✅ **Fully Operational** with fixed email template generation

### 📧 Email System
- **HTML Templates**: Responsive email design with proper CSS formatting
- **Personalization**: User name, topic preferences, and tone adaptation
- **Mindmap Integration**: SVG mindmaps embedded in emails
- **Delivery Tracking**: Success/failure monitoring with retry logic
- **Status**: ✅ **Fully Operational** - background variable error resolved

### 📢 Slack Integration
- **Team Communication**: Deliver newsletters directly to Slack channels
- **Portia AI Slack Tools**: Integration with Portia's Slack MCP tools
- **Rich Formatting**: Newsletter content formatted for Slack's messaging system
- **Channel Targeting**: Send to specific channels or users
- **Status**: ✅ **Fully Operational** - ready for team collaboration

## 🔧 How Portia AI Powers Our System

### 1. **Agent Orchestration**
```python
# Portia AI Agent Orchestrator
class NewsletterAgentOrchestrator:
    def __init__(self):
        self.research_agent = ResearchAgent()      # Portia-powered research
        self.writing_agent = WritingAgent()        # Portia-powered writing
        self.preference_agent = PreferenceAgent()  # Portia-powered learning
        self.custom_prompt_agent = CustomPromptAgent()  # Portia-powered NLP
```

### 2. **Multi-Agent Workflow**
```python
async def generate_newsletter_workflow(self, user_id: str, custom_prompt: str):
    """Complete newsletter generation using Portia AI agents"""
    
    # Step 1: Research Agent discovers content
    articles = await self.research_agent.execute_task("search_custom_prompt", context)
    
    # Step 2: Preference Agent provides user context  
    user_context = await self.preference_agent.execute_task("get_preferences", context)
    
    # Step 3: Writing Agent creates newsletter
    newsletter = await self.writing_agent.execute_task("generate_newsletter", context)
    
    # Step 4: Custom Prompt Agent enhances based on user request
    enhanced = await self.custom_prompt_agent.execute_task("process_prompt", context)
    
    return newsletter
```

### 3. **Intelligent Task Planning**
Each Portia AI agent creates sophisticated execution plans:

```python
# Example: Writing Agent Plan Creation
async def create_plan(self, context: Dict[str, Any]) -> Dict[str, Any]:
    """Create intelligent writing plan using Portia AI"""
    
    plan = {
        "task_sequence": [
            "analyze_user_preferences",    # Understand user context
            "structure_newsletter",        # Create content outline  
            "generate_sections",          # Write each section
            "enhance_with_rag",           # Add personalization
            "format_for_email",           # Create HTML template
            "generate_subject_lines"      # Create engaging subjects
        ],
        "context": context,
        "personalization_level": "high"
    }
    
    return plan
```

### 4. **Real-Time Agent Monitoring**
Our Portia AI agents include comprehensive monitoring:

```python
# Agent Health Monitoring
async def monitor_agent_health(self):
    """Monitor all Portia AI agents in real-time"""
    
    health_status = {
        "research_agent": await self.research_agent.health_check(),
        "writing_agent": await self.writing_agent.health_check(), 
        "preference_agent": await self.preference_agent.health_check(),
        "custom_prompt_agent": await self.custom_prompt_agent.health_check()
    }
    
    return health_status
```

## 📋 Complete API Reference

### 🔐 Authentication
```http
POST /auth/signup
POST /auth/verify-otp
```

### 📰 Newsletter Generation  
```http
POST /newsletters/generate              # Standard generation
POST /newsletters/generate-custom       # Custom prompt generation
POST /newsletters/send-now             # Immediate sending (email and/or Slack)
GET  /newsletters/analytics/{user_id}   # Performance analytics
```

### ⭐ Rating & Learning System
```http
POST /newsletters/rate                  # Quick star rating
POST /newsletters/rate-detailed         # Detailed feedback
GET  /newsletters/ratings/{user_id}     # Rating history
POST /newsletters/learn-preferences/{user_id}  # Trigger learning
```

### 🤖 Portia AI Agent Management
```http
POST /agents/test-all-agents           # Test all Portia agents
GET  /agents/agent-status              # Agent health status  
POST /agents/validate-integrations     # Service validation
```

### ⚙️ Scheduling & Automation
```http
GET  /newsletters/scheduler/status      # Scheduler status
POST /newsletters/scheduler/add-user    # Add to schedule
POST /newsletters/scheduler/trigger-immediate/{user_id}  # Manual trigger
```

### 📊 Monitoring & Analytics
```http
GET  /newsletters/monitoring/dashboard  # System health
GET  /newsletters/monitoring/agent/{name}  # Agent details
POST /newsletters/monitoring/start      # Start monitoring
```

### 📢 Slack Integration
```http
POST /newsletters/generate?send_slack=true  # Generate and send via Slack
POST /newsletters/send-now?send_slack=true  # Immediate send via Slack
```

## 🔧 Recent Updates & Fixes

### ✨ Version 2.0 - Production Ready (Current)

**🚀 Major Improvements:**
- **Email Delivery System**: Fixed critical "background" variable error in CSS templates
- **Mindmap Generation**: Added robust fallback system for PlanBuilder compatibility issues
- **Memory Service**: Implemented missing `store_user_data` and `get_user_data` methods
- **Newsletter Summaries**: Enhanced to generate AI insights instead of raw article links
- **UI Visibility**: Fixed text contrast issues across all Streamlit themes
- **Error Handling**: Comprehensive null safety and graceful degradation

**🐛 Bug Fixes:**
- ✅ Email template CSS formatting (background property errors)
- ✅ PlanBuilder "add_step" method compatibility
- ✅ MemoryService missing method implementations
- ✅ Newsletter content display in UI and email templates
- ✅ Mindmap SVG generation and email attachment
- ✅ Topic heading visibility across different themes

**📝 Technical Debt Resolved:**
- Cleaned up malformed CSS in email templates
- Added proper error handling for Portia AI agent failures
- Implemented graceful fallbacks for all AI operations
- Enhanced memory storage with proper key-value structure
- Fixed tuple return value handling in agent orchestrator

**📈 Performance Improvements:**
- Faster mindmap generation with efficient fallback systems
- Optimized email template rendering
- Better error recovery in multi-agent workflows
- Enhanced memory service with proper TTL management

## 🎆 What's Working Now

### ✅ Fully Operational Systems
1. **Complete Newsletter Generation Pipeline**
   - Research → Writing → Formatting → Email Delivery
   - All agents working with robust fallback mechanisms

2. **Email System**
   - HTML template generation ✅
   - Personalized content ✅
   - Mindmap embedding ✅
   - Delivery tracking ✅

3. **Mindmap Visualization**
   - Interactive zoom/pan controls ✅
   - SVG export functionality ✅
   - Email attachment system ✅
   - Fallback generation ✅

4. **User Interface**
   - Newsletter detail view ✅
   - Preference management ✅
   - Rating system ✅
   - Analytics dashboard ✅

5. **AI Agent Orchestration**
   - Multi-agent workflow ✅
   - Error recovery ✅
   - Memory persistence ✅
   - Performance monitoring ✅

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- PostgreSQL database (or SQLite for local development)
- API keys for integrations

### 1. Clone & Install
```bash
git clone <repository-url>
cd newsletter-ai

# Install dependencies using pip
pip install -r requirements.txt
```

### 2. Environment Configuration
Create a `.env` file in the root directory:

```env
# Core AI Services
GOOGLE_API_KEY=your_google_gemini_key  # Primary LLM
OPENAI_API_KEY=your_openai_key         # Fallback LLM
PORTIA_API_KEY=your_portia_key         # AI Agent Framework

# Research & Content
TAVILY_API_KEY=your_tavily_key         # Web search

# Email & Communication  
RESEND_API_KEY=your_resend_key         # Email delivery

# Slack Integration
SLACK_BOT_TOKEN=your_slack_bot_token   # Slack bot token
SLACK_APP_TOKEN=your_slack_app_token   # Slack app token
SLACK_CHANNEL_ID=your_channel_id       # Default Slack channel ID

# Storage & Memory
UPSTASH_REDIS_REST_URL=your_redis_url
UPSTASH_REDIS_REST_TOKEN=your_redis_token
UPSTASH_VECTOR_URL=your_vector_url
UPSTASH_VECTOR_TOKEN=your_vector_token

# Database (PostgreSQL recommended, SQLite fallback)
DATABASE_URL=postgresql://user:password@host:port/dbname
# Or for local development:
# DATABASE_URL=sqlite:///./newsletter_ai.db

# Security
SECRET_KEY=your-secret-key-change-in-production
```

### 3. Database Setup
The project uses a custom migration system. Choose one of the following options:

#### Option A: Create all tables (recommended for new setup)
```bash
python app/migrations/create_tables.py create
```

#### Option B: Reset database (drops and recreates all tables)
```bash
python app/migrations/create_tables.py reset
```

#### Option C: Seed with sample data (optional)
```bash
python app/migrations/seed_data.py
```

### 4. Start Services

#### Terminal 1: Start FastAPI backend
```bash
# Development server with auto-reload
uvicorn app.main:app --reload --port 8000

# Or use the run script
python run.py
```

#### Terminal 2: Start Streamlit frontend
```bash
streamlit run streamlit_app.py --server.port 8501
```

### 5. Verify Installation

#### Test API Connection
```bash
curl http://localhost:8000/
```

#### Test Core Services
```bash
# Test newsletter generation
curl -X POST "http://localhost:8000/api/v1/newsletters/generate" \
  -H "Content-Type: application/json" \
  -d '{"send_immediately": false}'

# Test email service (requires API keys)
curl -X POST "http://localhost:8000/api/v1/email/validate" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

#### Test System Health
```bash
# Check all service integrations
curl "http://localhost:8000/api/v1/newsletters/health"
```

### 6. Access the Application
- **Frontend (Streamlit)**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

## 🎮 User Journey

### 1. **Sign Up & Preferences** 
- Enter email, verify with OTP
- Select topics, tone, and frequency  
- System creates user profile

### 2. **Newsletter Generation**
Choose from three methods:
- **Automatic**: AI agents generate based on preferences
- **Scheduled**: Regular delivery (daily, weekly, monthly)
- **Custom Prompt**: Natural language requests

### 3. **Personalization Learning**
- Rate newsletters with 1-5 stars
- Provide feedback on topics you liked/disliked
- System automatically updates preferences via RAG

### 4. **Analytics & Insights**
- View reading patterns and engagement
- Get AI-powered recommendations  
- Export data and insights

## 🚨 Troubleshooting

### Recent Fixes (Current Version)

✅ **Fixed Issues:**
- Email delivery "background" variable error - resolved CSS formatting in templates
- PlanBuilder compatibility issues - added graceful fallback for mindmap generation  
- MemoryService missing methods - added `store_user_data` and `get_user_data` methods
- Mindmap SVG attachment functionality - working correctly in email templates
- Newsletter summary generation - now produces AI-generated insights instead of article links

### Common Issues

#### 1. Database Connection Errors
```bash
# Check if database exists and is accessible
python -c "from app.core.database import engine; print('Database connection:', engine)"

# Reset database if corrupted
python app/migrations/create_tables.py reset
```

#### 2. API Service Errors
```bash
# Test API health
curl http://localhost:8000/

# Check API logs with debug mode
uvicorn app.main:app --reload --log-level debug
```

#### 3. Email Delivery Issues
```bash
# Test email service configuration
python -c "
from app.services.email import email_service
print('RESEND API Key configured:', bool(email_service.api_key))
"

# Test email template generation
python -c "
from app.services.email import email_service
data = {'title': 'Test', 'sections': []}
html, plain, subject = email_service._create_personalized_newsletter(data)
print('Email generation: SUCCESS')
"
```

#### 4. Mindmap Generation Issues
```bash
# Test mindmap fallback generation
python -c "
import asyncio
from app.portia.mindmap_agent import mindmap_agent

async def test():
    context = {'newsletter_content': {'title': 'Test'}, 'articles': [], 'topics': []}
    result = await mindmap_agent._generate_fallback_mindmap(context)
    print('Mindmap generation: SUCCESS, length:', len(result))

asyncio.run(test())
"
```

#### 5. Memory Service Issues
```bash
# Test memory service connection
python -c "
import asyncio
from app.services.memory import memory_service

async def test():
    result = await memory_service.store_user_data('test', 'test_key', {'data': 'test'})
    print('Memory service: SUCCESS' if result else 'Memory service: NO REDIS')

asyncio.run(test())
"
```

#### 6. Missing Dependencies
```bash
# Reinstall all dependencies
pip install -r requirements.txt --force-reinstall

# Check specific packages
pip list | grep -E "(portia|resend|tavily|streamlit|fastapi)"
```

#### 7. Environment Variable Issues
```bash
# Check configuration loading
python -c "from app.core.config import settings; print('Config loaded successfully')"

# Verify required environment variables
python -c "
from app.core.config import settings
print('Google API Key:', bool(settings.GOOGLE_API_KEY))
print('Resend API Key:', bool(settings.RESEND_API_KEY))
print('Tavily API Key:', bool(settings.TAVILY_API_KEY))
print('Database URL:', bool(settings.DATABASE_URL))
"
```

### Environment Setup

#### Local Development (SQLite)
For local development without PostgreSQL:
```env
DATABASE_URL=sqlite:///./newsletter_ai.db
```

#### Production (PostgreSQL)
For production with cloud database:
```env
DATABASE_URL=postgresql://user:password@host:port/dbname
```

### Performance Tips

1. **Enable Redis Caching**: Set `UPSTASH_REDIS_URL` for better performance
2. **Use Vector Database**: Set `UPSTASH_VECTOR_URL` for RAG functionality
3. **Monitor Resources**: Check system health via Streamlit monitoring page
4. **Scale Workers**: Use multiple uvicorn workers for high load

```bash
# Multiple workers for production
uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000
```

## 🏗️ Architecture Highlights

### 🔄 Portia AI Workflow Engine
```mermaid
graph TB
    A[User Request] --> B[Agent Orchestrator]
    B --> C[Research Agent]
    B --> D[Preference Agent] 
    B --> E[Custom Prompt Agent]
    C --> F[Writing Agent]
    D --> F
    E --> F
    F --> G[Newsletter Output]
    G --> H[Email Delivery]
    G --> I[RAG Storage]
    I --> J[Learning Loop]
    J --> D
```

### 🧠 RAG-Powered Personalization
```mermaid
graph LR
    A[User Behavior] --> B[Vector Embeddings]
    B --> C[Semantic Search]
    C --> D[Content Recommendations]
    D --> E[Enhanced Generation]
    E --> F[Better Results]
    F --> A
```

### 📊 Real-Time Monitoring
```mermaid
graph TB
    A[Agent Health Monitor] --> B[Performance Metrics]
    B --> C[Error Detection]
    C --> D[Auto Recovery]
    D --> E[Status Dashboard]
    E --> F[Alert System]
```

## 🎯 Hackathon Achievements

### ✅ Technical Excellence
- **100% Task Completion**: All 16 planned tasks + bonus features
- **Production-Ready**: Full monitoring, error handling, and scaling
- **Modern Stack**: FastAPI, Streamlit, PostgreSQL, Vector DB
- **AI Integration**: Complete Portia AI agent framework

### 🚀 Innovation Highlights  
- **Multi-Agent Orchestration**: Sophisticated Portia AI workflow
- **RAG-Powered Learning**: Automatic preference optimization
- **Real-Time Personalization**: Dynamic content adaptation
- **Natural Language Interface**: Human-like prompt processing

### 📈 User Experience
- **Intuitive Design**: Modern, responsive interface
- **Zero Learning Curve**: Natural language interactions
- **Instant Gratification**: Real-time newsletter generation
- **Continuous Improvement**: AI learns from every interaction

## 🔮 Future Enhancements

### 📱 Potential Expansions
- **Mobile App**: Native iOS/Android applications
- **Social Integration**: Twitter, LinkedIn, RSS feed support
- **Team Features**: Collaborative newsletter creation
- **Enterprise**: Multi-tenant, white-label solutions

### 🤖 AI Enhancements
- **More Agents**: Social media, video, podcast research agents
- **Advanced RAG**: Multi-modal content understanding
- **Predictive Analytics**: Trend forecasting and content prediction
- **Voice Interface**: Audio-based newsletter consumption

## 🏆 Why This Project Wins

### 1. **Complete Portia AI Showcase**
We didn't just use Portia AI - we built a comprehensive multi-agent system that demonstrates the full power of the platform for complex, real-world applications.

### 2. **Production-Ready Quality**
This isn't a prototype. It's a fully functional system with monitoring, error handling, scheduling, and user management that could serve real users today.

### 3. **Innovative AI Application**
The combination of multi-agent orchestration, RAG-powered personalization, and natural language interfaces creates a truly intelligent system that learns and improves.

### 4. **Real Business Value**
Newsletter generation is a billion-dollar industry. Our system could revolutionize how content creators, marketers, and businesses communicate with their audiences.

## 👥 Team & Attribution

**Built for Portia AI Hackathon**
- **Framework**: Portia AI Multi-Agent System
- **Architecture**: Modern Python stack with AI-first design
- **Innovation**: RAG-powered personalization with continuous learning

## 📞 Support & Contact

For questions about this Portia AI hackathon project:
- 📧 Email: [Contact Information]
- 🐛 Issues: GitHub Issues
- 📖 Documentation: This README + in-code documentation

---

## 🙏 Acknowledgments

Special thanks to **Portia AI** for providing the powerful agent framework that made this sophisticated multi-agent system possible. The Portia AI platform enabled us to create a production-ready application that showcases the future of AI-powered content generation.

**This project demonstrates that with Portia AI, the impossible becomes inevitable.** 🚀

---

*Built with ❤️ and Portia AI for the hackathon community*
