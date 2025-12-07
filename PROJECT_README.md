# Toonify - AI Image Transformation Platform

## 🎨 Overview

Toonify is a full-stack AI-powered image transformation platform that converts user-uploaded images into cartoon-style outputs using OpenCV. The application supports multiple artistic styles including cartoon, pencil sketch, color pencil, edge preserve, and watercolor effects.

## 🏗️ Project Structure

```
project-root/
│
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── database.py          # Database configuration
│   │   ├── core/
│   │   │   ├── config.py        # Application settings
│   │   │   └── security.py      # JWT & password utilities
│   │   ├── models/
│   │   │   ├── user.py          # User model
│   │   │   ├── image_job.py     # Image job model
│   │   │   └── payment.py       # Payment model (future)
│   │   ├── schemas/
│   │   │   ├── user.py          # User Pydantic schemas
│   │   │   ├── image.py         # Image Pydantic schemas
│   │   │   └── payment.py       # Payment Pydantic schemas
│   │   ├── routers/
│   │   │   ├── auth.py          # Authentication routes
│   │   │   └── images.py        # Image processing routes
│   │   ├── services/
│   │   │   ├── auth_service.py  # Auth business logic
│   │   │   └── image_service.py # Image business logic
│   │   └── image_processing/
│   │       └── processor.py     # OpenCV image processor
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── streamlit_app.py         # Streamlit application
│   └── requirements.txt
│
├── storage/
│   ├── uploads/                 # Uploaded images
│   └── processed/               # Processed images
│
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL 14+
- pip (Python package manager)

### 1. Database Setup

```bash
# Create PostgreSQL database
psql -U postgres
CREATE DATABASE toonify;
\q
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
copy .env.example .env
# Edit .env with your database credentials and secret key

# Run the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup

```bash
# Open new terminal
cd frontend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run Streamlit app
streamlit run streamlit_app.py
```

### 4. Access the Application

- **Frontend**: http://localhost:8501
- **Backend API Docs**: http://localhost:8000/docs
- **Backend ReDoc**: http://localhost:8000/redoc

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/signup` | Register new user |
| POST | `/auth/login` | Login user |
| GET | `/auth/me` | Get current user profile |
| POST | `/auth/refresh` | Refresh access token |
| POST | `/auth/change-password` | Change password |

### Images
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/images/styles` | Get available styles |
| POST | `/images/upload` | Upload image |
| POST | `/images/{job_id}/process` | Process uploaded image |
| GET | `/images/{job_id}` | Get job details |
| GET | `/images/` | List user's jobs |
| GET | `/images/file/{job_id}/{type}` | Get image file |
| GET | `/images/download/{job_id}` | Download processed image |
| DELETE | `/images/{job_id}` | Delete job |

## 🎨 Available Styles

1. **Cartoon** - Classic cartoon effect with bold edges and flat colors
2. **Pencil Sketch** - Grayscale pencil sketch drawing effect
3. **Color Pencil** - Colored pencil artistic stylization
4. **Edge Preserve** - Edge-preserving smooth effect with enhanced details
5. **Watercolor** - Soft watercolor painting effect

## 🔧 Configuration

### Environment Variables (.env)

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/toonify

# JWT Settings
SECRET_KEY=your-super-secret-key-minimum-32-characters
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# File Storage
UPLOAD_DIR=storage/uploads
PROCESSED_DIR=storage/processed
MAX_FILE_SIZE=10485760
```

## 🔐 Security Features

- JWT-based authentication with access & refresh tokens
- Password hashing using bcrypt
- Password strength validation
- Rate limiting ready (configurable)
- Input validation with Pydantic

## 📋 Tech Stack

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **Frontend**: Streamlit
- **Image Processing**: OpenCV, NumPy
- **Authentication**: JWT (python-jose), Passlib

## 🛣️ Future Enhancements

- [ ] Payment integration (Razorpay/Stripe)
- [ ] Email verification
- [ ] Password reset via email
- [ ] AWS S3 storage support
- [ ] Batch processing
- [ ] Custom style parameters
- [ ] API rate limiting
- [ ] Admin dashboard

## 📄 License

MIT License
