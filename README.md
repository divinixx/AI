# AI-Based Image Transformation Tool for Cartoon Effect Generation

An end-to-end full-stack project using FastAPI, PostgreSQL, OpenCV, and Streamlit.

## Overview

This project is a web-based application that transforms user-uploaded photos into various cartoon-style effects such as classic cartoon, pencil sketch, and color pencil effects using OpenCV image processing pipelines. The system follows a service-oriented architecture with a FastAPI backend exposing REST APIs, a PostgreSQL database for persistence, and a Streamlit frontend that acts as a lightweight UI client consuming the backend APIs. Users can create accounts, upload images, preview different cartoon styles, view their history, and optionally unlock high-resolution downloads via a payment flow.

## Features

- User registration and login with secure password hashing and JWT-based authentication.  
- Image upload and selection of different cartoon transformation styles and parameters.  
- OpenCV-based image transformation pipeline with multiple effects (cartoon, sketch, color pencil, etc.).  
- Side-by-side preview of original and transformed images.  
- User-specific gallery/history of processed images.  
- Optional payment integration to unlock high-resolution downloads.  
- Dashboard with basic usage statistics and charts.

## Architecture

The application is structured as three main components:

1. FastAPI backend  
2. PostgreSQL database  
3. Streamlit frontend

The frontend never interacts with the database directly; it communicates only with the backend via HTTP APIs. The backend encapsulates all business logic, data access, and image processing. PostgreSQL is used as the primary data store for users, image jobs, and payments, while the file system (or object storage) holds the raw and processed images.

### Components

- Backend (FastAPI)  
  - REST API for auth, image job management, payment, and user history.  
  - OpenCV-based processing service for all cartoon effects.  
  - Integration with PostgreSQL via SQLAlchemy/SQLModel.  

- Database (PostgreSQL)  
  - Stores user accounts, image processing jobs, payment records, and metadata.  

- Frontend (Streamlit)  
  - Implements pages for login/registration, image upload and processing, gallery, and dashboard.  
  - Calls backend APIs and renders responses as UI components.

## Tech Stack

- Programming language: Python 3.10+  

- Backend:  
  - FastAPI  
  - Uvicorn (ASGI server)  
  - Pydantic v2 for request/response models  
  - HTTPX/requests for outbound HTTP calls (e.g., payment gateway)  

- Database and ORM:  
  - PostgreSQL  
  - SQLAlchemy 2.x (or SQLModel)  
  - asyncpg driver  
  - Alembic for migrations  

- Image Processing:  
  - OpenCV-Python  
  - NumPy  
  - Pillow (image format handling)  

- Frontend/UI:  
  - Streamlit (multi-page app)  

- Auth & Security:  
  - JWT (PyJWT or python-jose)  
  - passlib (bcrypt)  
  - Environment-based configuration (python-decouple / python-dotenv)  

- Optional Payments:  
  - Razorpay/Stripe (or similar) Python SDK in a payment service module  

- DevOps:  
  - Docker / docker-compose  
  - Logging via Python logging and SQLAlchemy engine logging  

## System Design

### Database Schema (PostgreSQL)

Suggested core tables:

- users  
  - id (UUID / integer PK)  
  - email (unique)  
  - password_hash  
  - full_name  
  - is_active  
  - is_admin  
  - created_at  
  - last_login  

- image_jobs  
  - id (UUID / integer PK)  
  - user_id (FK → users.id)  
  - original_path (string)  
  - output_path (string)  
  - style (enum: CARTOON, SKETCH, COLOR_PENCIL, etc.)  
  - params_json (JSONB)  
  - status (QUEUED, PROCESSING, DONE, FAILED)  
  - created_at  
  - processed_at  
  - error_message (nullable)  

- payments (optional if a paywall is included)  
  - id (UUID / integer PK)  
  - user_id (FK → users.id)  
  - job_id (FK → image_jobs.id)  
  - amount  
  - currency  
  - status (PENDING, SUCCESS, FAILED)  
  - gateway_reference  
  - created_at  
  - updated_at  

### Backend Structure (FastAPI)

Recommended project layout:

- app/  
  - main.py – app factory, router registration, middleware, CORS.  
  - config.py – environment-based settings (DB URL, JWT secret, payment keys).  
  - db.py – async engine, sessionmaker, database dependency.  
  - models/  
    - user.py  
    - image_job.py  
    - payment.py  
  - schemas/  
    - auth.py (UserCreate, Token, etc.)  
    - image.py (ImageJobCreate, ImageJobRead, etc.)  
    - payment.py  
  - services/  
    - auth.py (register, login, password hashing, token generation)  
    - image_processing.py (OpenCV pipelines)  
    - payments.py (gateway integration)  
  - routers/  
    - auth.py  
    - images.py  
    - payments.py  
    - users.py  

#### Core API Endpoints

- Auth  
  - POST /auth/register – create user account.  
  - POST /auth/login – issue JWT token.  
  - GET /users/me – get current user profile.  

- Images  
  - POST /images/transform – upload or reference an image, select style and parameters, create a processing job, trigger transformation, and return job metadata.  
  - GET /images/{job_id} – get job status and URLs for original/processed images.  
  - GET /images – list current user’s past jobs (for gallery/history).  

- Payments (optional)  
  - POST /payments/create – create a payment intent/order for a job.  
  - POST /payments/webhook or /payments/confirm – handle gateway callback and mark payment as SUCCESS/FAILED.  

### Image Processing (OpenCV)

Implement modular functions in app/services/image_processing.py:

- cartoon_effect(image, params):  
  - Convert to grayscale.  
  - Apply median blur.  
  - Use adaptive threshold for edges.  
  - Apply bilateral filter on color image.  
  - Combine edges and filtered color image with bitwise operations to get cartoon-like output.  

- pencil_sketch_effect(image, params):  
  - Grayscale conversion.  
  - Gaussian blur.  
  - Invert and divide to produce sketch effect.  

- color_pencil_effect(image, params):  
  - Combine or blend color image with sketch output using tunable weights.  

Parameters (blur kernel size, thresholds, bilateral filter sigma, etc.) are stored as JSON in params_json and exposed as sliders/inputs in the Streamlit UI.

## Frontend (Streamlit) Design

Use Streamlit as a multi-page application:

1. Authentication Page  
   - Login and registration forms.  
   - On successful login, store JWT token in st.session_state.  

2. Toonify Page (Main Processing)  
   - Image uploader for JPG/PNG.  
   - Dropdown to select style (Cartoon, Sketch, Color Pencil…).  
   - Sliders for effect parameters.  
   - Submit button that sends a request to /images/transform with token and file.  
   - Poll /images/{job_id} until status is DONE.  
   - Display original and processed images side-by-side.  
   - If paywall enabled, show a “Download HD” button tied to the payment flow.  

3. Gallery / Dashboard Page  
   - Call /images to display a history of processed images with small thumbnails.  
   - Filters by style, date range, and status.  
   - Simple charts (e.g., number of images per style over time) using Streamlit chart components.

All interactions use the backend APIs, so the UI remains thin and stateless beyond the JWT and some view state.

## Setup and Installation

1. Clone the repository  
   - git clone <your-repo-url>  
   - cd <your-repo>  

2. Create and activate a virtual environment  
   - python -m venv .venv  
   - source .venv/bin/activate (Linux/macOS)  
   - .venv\Scripts\activate (Windows)  

3. Install dependencies  
   - pip install -r requirements.txt  

4. Configure environment variables (.env)  
   - APP_ENV=local  
   - DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/toonify  
   - JWT_SECRET=your_jwt_secret  
   - JWT_ALGORITHM=HS256  
   - ACCESS_TOKEN_EXPIRE_MINUTES=60  
   - PAYMENT_PROVIDER_KEY=your_key (optional)  

5. Run database migrations  
   - alembic upgrade head  

6. Start backend (FastAPI)  
   - uvicorn app.main:app --reload  

7. Start frontend (Streamlit)  
   - streamlit run streamlit_app.py  

8. Access the app  
   - Open the Streamlit URL shown in the terminal (usually http://localhost:8501).  

## Usage

1. Register a new user account via the Streamlit auth page.  
2. Log in and ensure the token is stored (handled internally by Streamlit).  
3. Navigate to the Toonify page, upload an image, choose a cartoon style and tune parameters.  
4. Submit and wait for the processing to complete; preview the original and transformed images.  
5. Optionally proceed through the payment flow to unlock high-resolution download (if enabled).  
6. Explore the Gallery/Dashboard page to view and re-download previously processed images.

## Testing

- Unit tests for image processing functions to validate outputs and check for runtime errors.  
- API tests for endpoints (auth, image jobs, payments) using a test database.  
- Basic integration tests for end-to-end flow: register → login → upload → transform → list history.

## Roadmap

- Add additional artistic filters using more advanced OpenCV or deep learning models.  
- Introduce background task processing for heavy jobs (Celery/RQ).  
- Add rate limiting and quotas per user.  
- Implement full CI/CD pipeline and cloud deployment (e.g., Docker + managed Postgres).  

This README can be dropped directly into your repository as README.md and iteratively refined as the implementation evolves.

[1](https://github.com/JayThibs/fastapi-streamlit-postgresql-ml-template)
[2](https://www.evidentlyai.com/blog/fastapi-tutorial)
[3](https://pybit.es/articles/my-experience-building-a-fastapi-streamlit-app/)
[4](https://fastapi.tiangolo.com/project-generation/)
[5](https://www.linkedin.com/posts/rohitanshu-dhar_learningjourney-streamlit-fastapi-activity-7360907041336397824-GckS)
[6](https://github.com/rafaeljurkfitz/crud-fastapi-postgres-streamlit)
[7](https://blog.devgenius.io/zero-friction-fastapi-postgres-template-2025-for-every-side-project-69d4b30f7d89)
[8](http://codesandbox.io/p/github/DanielBodnar/readme-ai)
[9](https://pypi.org/project/readmeai/0.5.2/)