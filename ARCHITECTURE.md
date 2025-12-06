# 🏗️ Project Architecture - AI Image Transformation Tool

## Overview

This document describes the modular architecture of the AI-Based Image Transformation Tool for Cartoon Effect Generation.

---

## 📊 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (Streamlit)                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   Auth Page  │  │ Toonify Page │  │ Gallery Page │  │  Dashboard   │        │
│  │  Login/Reg   │  │   Transform  │  │   History    │  │    Stats     │        │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘        │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        │ HTTP/REST API
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              BACKEND (FastAPI)                                   │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                           API Layer (Routers)                            │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐        │   │
│  │  │    Auth    │  │   Images   │  │  Payments  │  │   Users    │        │   │
│  │  │  /auth/*   │  │  /images/* │  │ /payments/*│  │  /users/*  │        │   │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘        │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                        │                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                         Service Layer (Business Logic)                   │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐        │   │
│  │  │  Auth Svc  │  │Image Proc  │  │ Payment Svc│  │ ImageJob   │        │   │
│  │  │  JWT/Pass  │  │  OpenCV    │  │  Gateway   │  │   CRUD     │        │   │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘        │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                        │                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                            Data Layer (Models)                           │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐                         │   │
│  │  │    User    │  │  ImageJob  │  │  Payment   │                         │   │
│  │  └────────────┘  └────────────┘  └────────────┘                         │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        │ SQLAlchemy Async
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            DATABASE (PostgreSQL)                                 │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐                                │
│  │   users    │  │ image_jobs │  │  payments  │                                │
│  └────────────┘  └────────────┘  └────────────┘                                │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              FILE STORAGE                                        │
│  ┌────────────────────────┐  ┌────────────────────────┐                        │
│  │      /uploads/         │  │     /processed/        │                        │
│  │   Original Images      │  │   Transformed Images   │                        │
│  └────────────────────────┘  └────────────────────────┘                        │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
AI/
├── README.md                    # Project overview & setup instructions
├── ARCHITECTURE.md              # This file - architecture documentation
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── docker-compose.yml           # Docker orchestration
├── alembic.ini                  # Alembic migrations config
│
├── backend/                     # FastAPI Backend Application
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # App factory, router registration
│   │   ├── config.py            # Environment-based settings
│   │   ├── db.py                # Database engine & session
│   │   ├── dependencies.py      # Shared FastAPI dependencies
│   │   │
│   │   ├── models/              # SQLAlchemy ORM Models
│   │   │   ├── __init__.py
│   │   │   ├── user.py          # User model
│   │   │   ├── image_job.py     # ImageJob model + enums
│   │   │   └── payment.py       # Payment model
│   │   │
│   │   ├── schemas/             # Pydantic Request/Response Schemas
│   │   │   ├── __init__.py
│   │   │   ├── auth.py          # Auth schemas (UserCreate, Token, etc.)
│   │   │   ├── image.py         # Image schemas (JobCreate, JobResponse)
│   │   │   └── payment.py       # Payment schemas
│   │   │
│   │   ├── routers/             # API Endpoints (Controllers)
│   │   │   ├── __init__.py
│   │   │   ├── auth.py          # /auth/* endpoints
│   │   │   ├── users.py         # /users/* endpoints
│   │   │   ├── images.py        # /images/* endpoints
│   │   │   └── payments.py      # /payments/* endpoints
│   │   │
│   │   └── services/            # Business Logic Layer
│   │       ├── __init__.py
│   │       ├── auth.py          # Authentication & JWT service
│   │       ├── image_job.py     # Image job CRUD operations
│   │       ├── image_processing.py  # OpenCV transformations
│   │       └── payments.py      # Payment gateway integration
│   │
│   ├── migrations/              # Alembic database migrations
│   │   ├── versions/
│   │   └── env.py
│   │
│   └── tests/                   # Backend tests
│       ├── __init__.py
│       ├── conftest.py
│       ├── test_auth.py
│       ├── test_images.py
│       └── test_payments.py
│
├── frontend/                    # Streamlit Frontend Application
│   ├── streamlit_app.py         # Main entry point
│   ├── config.py                # Frontend configuration
│   │
│   ├── api/                     # API Client Module
│   │   ├── __init__.py
│   │   └── client.py            # Backend API client
│   │
│   ├── components/              # Reusable UI Components
│   │   ├── __init__.py
│   │   ├── auth_forms.py        # Login/Register forms
│   │   ├── image_upload.py      # Image uploader component
│   │   ├── image_display.py     # Side-by-side image display
│   │   └── style_selector.py    # Style & params selector
│   │
│   ├── pages/                   # Streamlit Multi-Page App
│   │   ├── 1_🎨_Toonify.py      # Main transformation page
│   │   ├── 2_🖼️_Gallery.py      # Image history/gallery
│   │   └── 3_📊_Dashboard.py    # Stats and charts
│   │
│   └── utils/                   # Frontend utilities
│       ├── __init__.py
│       └── session.py           # Session state management
│
├── uploads/                     # Original uploaded images
├── processed/                   # Transformed images
│
└── scripts/                     # Utility scripts
    ├── init_db.py               # Database initialization
    └── seed_data.py             # Seed test data
```

---

## 🧩 Module Breakdown

### Module 1: Core Infrastructure

| Component | File | Purpose |
|-----------|------|---------|
| Configuration | `backend/app/config.py` | Environment variables, settings |
| Database | `backend/app/db.py` | Async engine, session factory |
| Dependencies | `backend/app/dependencies.py` | Shared FastAPI dependencies |
| Main App | `backend/app/main.py` | App factory, CORS, routers |

### Module 2: Authentication & Users

| Layer | File | Purpose |
|-------|------|---------|
| Model | `models/user.py` | User ORM model |
| Schema | `schemas/auth.py` | UserCreate, Token, UserResponse |
| Service | `services/auth.py` | JWT, password hashing, user ops |
| Router | `routers/auth.py` | /auth/register, /auth/login |
| Router | `routers/users.py` | /users/me, profile management |

**Key Features:**
- JWT access & refresh tokens
- Bcrypt password hashing
- Email-based authentication
- Profile update & password change

### Module 3: Image Processing

| Layer | File | Purpose |
|-------|------|---------|
| Model | `models/image_job.py` | ImageJob ORM, Style/Status enums |
| Schema | `schemas/image.py` | JobCreate, JobResponse, Params |
| Service | `services/image_processing.py` | OpenCV transformation pipelines |
| Service | `services/image_job.py` | Job CRUD, file management |
| Router | `routers/images.py` | /images/transform, /images/* |

**Supported Effects:**
| Style | Description |
|-------|-------------|
| `CARTOON` | Classic cartoon effect with edge detection |
| `SKETCH` | Pencil sketch (black & white) |
| `COLOR_PENCIL` | Colored pencil drawing effect |
| `OIL_PAINTING` | Oil painting wuylization |
| `WATERCOLOR` | Watercolor paint effect |
| `POP_ART` | Andy Warhol-style pop art |

### Module 4: Payments (Optional)

| Layer | File | Purpose |
|-------|------|---------|
| Model | `models/payment.py` | Payment ORM model |
| Schema | `schemas/payment.py` | PaymentCreate, PaymentIntent |
| Service | `services/payments.py` | Stripe/Razorpay integration |
| Router | `routers/payments.py` | /payments/create, webhook |

**Flow:**
1. User requests HD download
2. Create payment intent → gateway
3. Frontend handles payment UI
4. Webhook confirms payment
5. Unlock HD download for job

### Module 5: Frontend (Streamlit)

| Component | File | Purpose |
|-----------|------|---------|
| Entry Point | `streamlit_app.py` | Main app, auth gate |
| API Client | `api/client.py` | Backend HTTP client |
| Auth UI | `components/auth_forms.py` | Login/register forms |
| Transform UI | `pages/1_🎨_Toonify.py` | Image transformation |
| Gallery UI | `pages/2_🖼️_Gallery.py` | Image history |
| Dashboard UI | `pages/3_📊_Dashboard.py` | Usage statistics |

---

## 🔄 Data Flow

### Authentication Flow

```
┌─────────┐     POST /auth/login      ┌─────────┐     verify      ┌─────────┐
│ Frontend│ ──────────────────────────▶│ Backend │ ───────────────▶│   DB    │
│         │◀────────────────────────── │         │◀─────────────── │         │
└─────────┘     JWT Token              └─────────┘     User        └─────────┘
     │
     │ Store token in session_state
     ▼
┌─────────┐     Authorization: Bearer  ┌─────────┐
│ Frontend│ ───────────────────────────▶│ Backend │
│         │     (all subsequent calls)  │         │
└─────────┘                             └─────────┘
```

### Image Transformation Flow

```
┌─────────┐   1. Upload Image    ┌─────────┐  2. Save File   ┌─────────┐
│ Frontend│ ────────────────────▶│ Backend │ ───────────────▶│ Storage │
│         │   + Style + Params   │         │                 │/uploads │
└─────────┘                      └─────────┘                 └─────────┘
                                      │
                                      │ 3. Create Job (QUEUED)
                                      ▼
                                 ┌─────────┐
                                 │   DB    │
                                 │image_job│
                                 └─────────┘
                                      │
                                      │ 4. Process (OpenCV)
                                      ▼
┌─────────┐   6. Job Response    ┌─────────┐  5. Save Output  ┌─────────┐
│ Frontend│◀────────────────────│ Backend │ ───────────────▶│ Storage │
│         │   status=DONE       │         │                 │/processed│
└─────────┘                      └─────────┘                 └─────────┘
```

---

## 🔐 Security Architecture

### Authentication
- **Method**: JWT Bearer Tokens
- **Access Token**: 60 min expiry
- **Refresh Token**: 7 days expiry
- **Password**: Bcrypt hashing (work factor 12)

### Authorization
- All `/images/*`, `/users/*`, `/payments/*` require valid JWT
- User can only access their own resources
- Admin flag for future admin features

### CORS
- Configured origins: localhost:8501 (Streamlit)
- Credentials: enabled
- Methods: all
- Headers: all

---

## 🗄️ Database Schema

### Entity Relationship Diagram

```
┌─────────────────────┐
│       users         │
├─────────────────────┤
│ id (PK)             │
│ uuid                │
│ email (unique)      │
│ password_hash       │
│ full_name           │
│ is_active           │
│ is_admin            │
│ created_at          │
│ updated_at          │
│ last_login          │
└─────────────────────┘
          │
          │ 1:N
          ▼
┌─────────────────────┐
│     image_jobs      │
├─────────────────────┤
│ id (PK)             │
│ uuid                │
│ user_id (FK)        │──────┐
│ original_filename   │      │
│ original_path       │      │
│ output_path         │      │
│ style (enum)        │      │
│ params_json (JSONB) │      │
│ status (enum)       │      │
│ error_message       │      │
│ is_hd_unlocked      │      │
│ created_at          │      │
│ processed_at        │      │
└─────────────────────┘      │
          │                  │
          │ 1:1              │
          ▼                  │
┌─────────────────────┐      │
│      payments       │      │
├─────────────────────┤      │
│ id (PK)             │      │
│ uuid                │      │
│ user_id (FK)        │◀─────┘
│ job_id (FK)         │
│ amount              │
│ currency            │
│ status (enum)       │
│ gateway_reference   │
│ gateway_response    │
│ created_at          │
│ updated_at          │
└─────────────────────┘
```

---

## 🚀 API Endpoints Summary

### Authentication (`/auth`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Create new user account |
| POST | `/auth/login` | Get JWT tokens |
| POST | `/auth/refresh` | Refresh access token |

### Users (`/users`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users/me` | Get current user profile |
| PUT | `/users/me` | Update profile |
| POST | `/users/me/change-password` | Change password |

### Images (`/images`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/images/transform` | Upload & transform image |
| GET | `/images` | List user's jobs (paginated) |
| GET | `/images/{uuid}` | Get job details |
| GET | `/images/{uuid}/original` | Download original image |
| GET | `/images/{uuid}/processed` | Download processed image |
| DELETE | `/images/{uuid}` | Delete job & files |

### Payments (`/payments`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/payments/create` | Create payment intent |
| POST | `/payments/confirm` | Confirm payment |
| POST | `/payments/webhook` | Gateway webhook handler |

---

## 🔧 Configuration

### Environment Variables

```env
# Application
APP_ENV=local
DEBUG=true

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/toonify

# JWT
JWT_SECRET=your-super-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=["http://localhost:8501"]

# File Storage
UPLOAD_DIR=uploads
PROCESSED_DIR=processed
MAX_FILE_SIZE_MB=10
ALLOWED_EXTENSIONS=["jpg","jpeg","png","webp"]

# Image Processing
DEFAULT_OUTPUT_QUALITY=85
MAX_IMAGE_DIMENSION=4096

# Payments (Optional)
PAYMENT_PROVIDER=stripe
PAYMENT_PROVIDER_KEY=sk_test_xxx
PAYMENT_PROVIDER_SECRET=xxx
PAYMENT_WEBHOOK_SECRET=whsec_xxx
```

---

## 🐳 Docker Architecture

```yaml
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
    depends_on: [db]
    volumes:
      - ./uploads:/app/uploads
      - ./processed:/app/processed

  frontend:
    build: ./frontend
    ports: ["8501:8501"]
    depends_on: [backend]

  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

---

## 📈 Future Enhancements

1. **Background Processing**: Celery/RQ for async job processing
2. **Object Storage**: AWS S3/Azure Blob for scalable file storage
3. **Caching**: Redis for session and API response caching
4. **Deep Learning**: Add AI-powered style transfer effects
5. **Rate Limiting**: Per-user API rate limits
6. **Monitoring**: Prometheus + Grafana dashboards
7. **CI/CD**: GitHub Actions pipeline

---

*Last Updated: December 2024*
