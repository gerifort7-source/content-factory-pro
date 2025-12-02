# 🏭 Content Factory Pro

**AI-powered content generation and scheduling platform with Telegram integration, admin panel, and advanced analytics.**

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## ✨ Features

### 📝 Content Generation
- **AI-Powered Generation**: Integration with OpenAI (GPT-4) and Anthropic (Claude)
- **Multi-Language Support**: Russian, English, and other languages
- **Customizable Tone**: Professional, casual, friendly, technical
- **SEO Optimization**: Built-in SEO suggestions and optimization

### 📅 Content Scheduling
- **Advanced Scheduling**: Schedule posts for specific dates and times
- **Recurring Posts**: Set up automated recurring content
- **Queue Management**: Manage content queue with priority levels
- **Timezone Support**: Full timezone support for global scheduling

### 🤖 Telegram Integration
- **Automated Publishing**: Direct integration with Telegram Bot API
- **Channel Management**: Manage multiple Telegram channels
- **Message Templates**: Predefined templates for quick publishing
- **Analytics Tracking**: Track post engagement and performance

### 🎛️ Admin Panel
- **FastAPI-based API**: RESTful API for all operations
- **Web Dashboard**: Interactive web interface for management
- **User Authentication**: JWT-based authentication
- **Role-Based Access**: Admin, moderator, and user roles

### 📊 Analytics & Reporting
- **Performance Metrics**: Track views, likes, shares, and comments
- **Content Analytics**: Analyze which types of content perform best
- **Audience Insights**: Understand your audience demographics
- **Export Reports**: Generate and export analytics reports

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL 12+
- Redis 6+
- Telegram Bot Token
- OpenAI API Key (optional)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/gerifort7-source/content-factory-pro.git
cd content-factory-pro
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your credentials
```

5. **Initialize database**
```bash
alembic upgrade head
```

6. **Run application**
```bash
uvicorn app.main:app --reload --port 8000
```

## 📁 Project Structure

```
content-factory-pro/
├── core/                      # Core configuration
│   ├── config.py             # Application settings
│   └── __init__.py
├── app/                       # Main application
│   ├── main.py               # Application entry point
│   ├── api/                  # API routes
│   │   ├── content.py        # Content endpoints
│   │   ├── scheduler.py      # Scheduling endpoints
│   │   ├── telegram.py       # Telegram integration
│   │   └── analytics.py      # Analytics endpoints
│   ├── services/             # Business logic
│   │   ├── content_generator.py
│   │   ├── telegram_handler.py
│   │   ├── scheduler_service.py
│   │   └── analytics_service.py
│   ├── models/               # Database models
│   ├── schemas/              # Pydantic schemas
│   └── admin/                # Admin panel
├── database/                 # Database
│   ├── models.py            # SQLAlchemy models
│   └── session.py           # DB session management
├── migrations/              # Alembic migrations
├── tests/                   # Unit & integration tests
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
└── docker-compose.yml      # Docker compose config
```

## 🔧 Configuration

Edit `.env` file with your settings:

```env
# Telegram
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHANNEL_ID=-1001234567890

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/content_factory

# Redis
REDIS_URL=redis://localhost:6379/0

# Admin
ADMIN_USERNAME=admin
ADMIN_PASSWORD=secure_password
```

## 📚 API Documentation

API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access at http://localhost:8000
```

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app
```

## 📝 Usage Examples

### Generate Content
```python
from app.services.content_generator import ContentGenerator

generator = ContentGenerator()
content = await generator.generate(
    topic="Python programming",
    tone="technical",
    language="en",
    max_length=500
)
```

### Schedule Post
```python
from app.services.scheduler_service import SchedulerService

scheduler = SchedulerService()
scheduled_post = await scheduler.schedule_post(
    content="Hello, World!",
    scheduled_time="2024-01-15 10:00",
    channel_id=-1001234567890
)
```

### Get Analytics
```python
from app.services.analytics_service import AnalyticsService

analytics = AnalyticsService()
stats = await analytics.get_post_stats(
    post_id=1,
    date_from="2024-01-01",
    date_to="2024-01-31"
)
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**gerifort7-source** - [GitHub](https://github.com/gerifort7-source)

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- Telegram Bot API for integration
- OpenAI and Anthropic for AI capabilities
- PostgreSQL and Redis communities

## 📞 Support

For support, email support@contentfactory.local or open an issue on GitHub.

## 🗂️ Project Status

- [x] Core infrastructure
- [x] Configuration management
- [ ] Content generator module
- [ ] Telegram bot handler
- [ ] Database models
- [ ] API routes
- [ ] Admin panel UI
- [ ] Analytics dashboard
- [ ] Deployment guide
- [ ] Comprehensive tests

---

**Made with ❤️ by gerifort7-source**
