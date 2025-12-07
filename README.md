<div align="center">

# 🎨 Toonify

### *Transform Reality into Art with AI*

[![FastAPI](https://img.shields.io/badge/FastAPI-0.124.0-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40.0-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.12.0-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

**Production-ready AI Image Transformation Platform** | Turn your photos into stunning cartoon masterpieces in seconds

[Quick Start](#-quick-start) • [Documentation](#-project-structure) • [API Reference](#-api-endpoints) • [Features](#-features)

![Toonify Banner](https://via.placeholder.com/1200x300/667eea/ffffff?text=Toonify+-+AI+Image+Transformation+Platform)

</div>

---

## 🌟 Overview

**Toonify** is an enterprise-grade, full-stack AI image transformation platform that converts real-world photographs into artistic cartoon-style images using advanced OpenCV algorithms. Built with modern web technologies and designed for scalability, security, and performance.

### 🎯 What Makes Toonify Special?

- **🚀 Lightning Fast** - Process images in 5-15 seconds with optimized OpenCV pipelines
- **🎨 5 Artistic Styles** - Cartoon, Pencil Sketch, Color Pencil, Edge Preserve, Watercolor
- **🔒 Enterprise Security** - JWT authentication, bcrypt password hashing, SQL injection protection
- **📱 Modern UI/UX** - Beautiful gradient-based interface with real-time progress tracking
- **⚡ Async Processing** - Non-blocking background tasks with FastAPI BackgroundTasks
- **📊 Advanced Filtering** - Gallery with status, style, and date filters
- **🔄 Side-by-Side Comparison** - View before/after transformations instantly
- **💾 Persistent Storage** - Local file system with PostgreSQL metadata management

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🔐 Authentication System
- ✅ User registration & login
- ✅ JWT-based access tokens
- ✅ Secure password hashing (bcrypt)
- ✅ Session management
- ✅ Password strength validation
- ✅ Email verification ready

</td>
<td width="50%">

### 🖼️ Image Processing
- ✅ Multi-style transformations
- ✅ Real-time processing status
- ✅ Background task processing
- ✅ Before/after comparison
- ✅ High-quality output (PNG)
- ✅ Supports JPG, PNG, WEBP

</td>
</tr>
<tr>
<td width="50%">

### 📚 Gallery Management
- ✅ Filter by status & style
- ✅ Sort by date (newest/oldest)
- ✅ Grid view with thumbnails
- ✅ Quick view & download
- ✅ Processing status tracking
- ✅ Error message display

</td>
<td width="50%">

### 🎨 Available Styles
- **Cartoon** - Bold edges, vibrant colors
- **Pencil Sketch** - Grayscale drawing
- **Color Pencil** - Artistic strokes
- **Edge Preserve** - Sharp details
- **Watercolor** - Soft painting

</td>
</tr>
</table>

---

## 🏗️ Architecture

### System Design

```
┌─────────────────────────────────────────────────────────────────┐
│                        🌐 Frontend Layer                         │
│                     Streamlit (Port 8501)                        │
│  • Login/Signup UI    • Image Upload    • Style Selection       │
│  • Progress Tracking  • Gallery View    • Download Manager      │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      │ HTTP/REST API
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                        ⚡ Backend Layer                          │
│                     FastAPI (Port 8000)                          │
│  • JWT Authentication  • Image Processing API                   │
│  • Background Tasks    • File Management                        │
│  • Error Handling      • Rate Limiting Ready                    │
└─────────────────────┬──────────────┬────────────────────────────┘
                      │              │
            ┌─────────▼────┐    ┌────▼──────┐
            │  PostgreSQL  │    │   OpenCV  │
            │   Database   │    │ Processor │
            └──────────────┘    └─────┬─────┘
                                      │
                                ┌─────▼──────┐
                                │   File     │
                                │  Storage   │
                                └────────────┘
```

### 🔧 Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Streamlit | Interactive web interface with real-time updates |
| **Backend** | FastAPI | High-performance async REST API |
| **Database** | PostgreSQL | Relational data storage with ACID compliance |
| **Image Processing** | OpenCV | Advanced computer vision algorithms |
| **Authentication** | JWT + bcrypt | Secure token-based auth with password hashing |
| **ORM** | SQLAlchemy | Database abstraction and migrations |
| **Validation** | Pydantic | Request/response data validation |
| **File Storage** | Local Filesystem | Image upload and processed file storage |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- PostgreSQL 14+ (or use SQLite for quick testing)
- 4GB RAM minimum
- 1GB free disk space

### 📦 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/toonify.git
cd toonify

# Setup Backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials

# Run migrations (if using PostgreSQL)
alembic upgrade head

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# In a new terminal - Setup Frontend
cd ../frontend
pip install -r requirements.txt

# Start frontend
streamlit run streamlit_app.py
```

### 🔑 Environment Configuration

Create `.env` file in `backend/` directory:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/toonify
# Or use SQLite: DATABASE_URL=sqlite:///./toonify.db

# JWT Settings
SECRET_KEY=your-super-secret-key-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# File Storage
UPLOAD_DIR=storage/uploads
PROCESSED_DIR=storage/processed
MAX_FILE_SIZE=10485760
```

### 🎯 Access the Application

- **Frontend UI**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📁 Project Structure

```
toonify/
├── backend/                      # FastAPI Backend
│   ├── app/
│   │   ├── core/                # Core configurations
│   │   │   ├── config.py       # Application settings
│   │   │   └── security.py     # JWT & password utilities
│   │   ├── models/              # SQLAlchemy models
│   │   │   ├── user.py         # User model
│   │   │   └── image_job.py    # Image job model
│   │   ├── schemas/             # Pydantic schemas
│   │   │   ├── user.py         # User DTOs
│   │   │   └── image.py        # Image DTOs
│   │   ├── routers/             # API routes
│   │   │   ├── auth.py         # Authentication endpoints
│   │   │   └── images.py       # Image processing endpoints
│   │   ├── services/            # Business logic
│   │   │   ├── auth_service.py
│   │   │   └── image_service.py
│   │   ├── image_processing/    # OpenCV processing
│   │   │   └── processor.py    # Image transformation engine
│   │   ├── database.py          # Database configuration
│   │   └── main.py              # FastAPI application
│   ├── storage/                 # File storage
│   │   ├── uploads/            # Original images
│   │   └── processed/          # Transformed images
│   ├── alembic/                # Database migrations
│   ├── tests/                  # Unit & integration tests
│   ├── requirements.txt
│   └── .env
│
├── frontend/                    # Streamlit Frontend
│   ├── streamlit_app.py        # Main application
│   └── requirements.txt
│
└── README.md                    # This file
```

---

## 🔌 API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/signup` | Register new user | ❌ |
| POST | `/auth/login` | User login | ❌ |
| POST | `/auth/refresh` | Refresh access token | ❌ |
| GET | `/auth/me` | Get current user | ✅ |
| POST | `/auth/change-password` | Change password | ✅ |

### Image Processing

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/images/styles` | Get available styles | ❌ |
| POST | `/images/upload` | Upload image | ✅ |
| POST | `/images/{job_id}/process` | Start processing | ✅ |
| GET | `/images/{job_id}` | Get job status | ✅ |
| GET | `/images/` | List user's jobs | ✅ |
| GET | `/images/file/{job_id}/{type}` | Get image file | ✅ |
| GET | `/images/download/{job_id}` | Download processed image | ✅ |

### Example Requests

```bash
# Register User
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "SecurePass123!",
    "full_name": "John Doe"
  }'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user@example.com", "password": "SecurePass123!"}'

# Upload Image
curl -X POST "http://localhost:8000/images/upload?style=cartoon" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@photo.jpg"

# Check Status
curl -X GET http://localhost:8000/images/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 🎨 Image Processing Pipeline

### Transformation Algorithms

#### 1. 🎬 Cartoon Effect
- Bilateral filtering for edge preservation
- K-means color quantization (8 colors)
- Adaptive edge detection with morphological operations
- Edge + color fusion with optimized blending

#### 2. ✏️ Pencil Sketch
- Gaussian blur for smoothing
- Inverted grayscale division technique
- Dodge blending mode simulation
- Enhanced contrast for sketch effect

#### 3. 🖍️ Color Pencil
- Edge detection with Canny
- Color preservation with HSV conversion
- Pencil texture simulation
- Color + edge overlay blending

#### 4. 🔲 Edge Preserve
- Bilateral filter (advanced)
- Mean shift filtering
- Detail enhancement
- Smooth + sharp detail fusion

#### 5. 💧 Watercolor
- Multi-level bilateral filtering
- Median blur for watercolor effect
- Saturation enhancement
- Soft edge blending

### Performance Metrics

| Metric | Value |
|--------|-------|
| Average Processing Time | 5-15 seconds |
| Max Image Size | 10MB |
| Supported Resolutions | Up to 4000x4000px |
| Output Format | PNG (lossless) |
| Color Space | RGB |

---

## 🔒 Security Features

- **Password Security**: Bcrypt hashing with salt, 50-character limit
- **JWT Authentication**: Secure token-based authentication with expiry
- **SQL Injection Protection**: SQLAlchemy ORM with parameterized queries
- **CORS Configuration**: Configurable cross-origin resource sharing
- **Rate Limiting**: Ready for implementation with middleware
- **File Validation**: MIME type and size validation on uploads
- **Error Handling**: Secure error messages without sensitive data leakage

---

## 📊 Database Schema

```sql
-- Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Image Jobs Table
CREATE TABLE image_jobs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    original_filename VARCHAR(255) NOT NULL,
    original_path VARCHAR(500) NOT NULL,
    processed_path VARCHAR(500),
    comparison_path VARCHAR(500),
    style VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_image_jobs_user_id ON image_jobs(user_id);
CREATE INDEX idx_image_jobs_status ON image_jobs(status);
CREATE INDEX idx_users_email ON users(email);
```

---

## 🧪 Testing

```bash
# Run all tests
cd backend
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v

# Run integration tests
pytest tests/integration/ -v
```

---

## 🚀 Deployment

### Docker Deployment

```dockerfile
# Backend Dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: toonify
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: yourpassword
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - postgres
    environment:
      DATABASE_URL: postgresql://postgres:yourpassword@postgres:5432/toonify

  frontend:
    build: ./frontend
    ports:
      - "8501:8501"
    depends_on:
      - backend

volumes:
  postgres_data:
```

### Production Checklist

- [ ] Set strong `SECRET_KEY` in environment variables
- [ ] Configure PostgreSQL with connection pooling
- [ ] Enable HTTPS with SSL certificates
- [ ] Set up reverse proxy (Nginx/Caddy)
- [ ] Configure CDN for static files
- [ ] Enable database backups
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Configure log aggregation
- [ ] Implement rate limiting
- [ ] Set up CI/CD pipeline

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide for Python code
- Write unit tests for new features
- Update documentation for API changes
- Use type hints for function signatures
- Add docstrings for public methods

---

## 🐛 Troubleshooting

### Common Issues

**1. Database Connection Failed**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Verify credentials in .env file
DATABASE_URL=postgresql://user:pass@localhost:5432/toonify
```

**2. Image Processing Timeout**
```bash
# Check backend logs for errors
# Verify storage directories exist and have write permissions
chmod -R 755 storage/

# Check if OpenCV is properly installed
python -c "import cv2; print(cv2.__version__)"
```

**3. Frontend Can't Connect to Backend**
```bash
# Verify backend is running
curl http://localhost:8000/docs

# Check if API_BASE_URL in frontend matches backend
# frontend/streamlit_app.py: API_BASE_URL = "http://localhost:8000"
```

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

**Made with ❤️ by Developers, for Developers**

- **Lead Developer**: Your Name
- **Contributors**: [See all contributors](https://github.com/yourusername/toonify/graphs/contributors)

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [Streamlit](https://streamlit.io/) - Beautiful data apps
- [OpenCV](https://opencv.org/) - Computer vision library
- [PostgreSQL](https://www.postgresql.org/) - Powerful database
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation

---

## 📞 Support

- **Documentation**: [Full Docs](https://docs.toonify.app)
- **Issues**: [GitHub Issues](https://github.com/yourusername/toonify/issues)
- **Email**: support@toonify.app
- **Discord**: [Join our community](https://discord.gg/toonify)

---

<div align="center">

### ⭐ Star this repo if you find it useful!

**Built with modern technologies and best practices for production deployment**

Made with 💜 by Developers who care about code quality

[⬆ Back to Top](#-toonify)

</div>
