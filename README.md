📌 Detailed Project Prompt (Industry-Level Specification)
Project: AI-Based Image Transformation Tool for Cartoon Effect Generation — “Toonify”
1. Project Overview

Build a full-stack, production-ready AI Image Transformation Platform that converts user-uploaded images into cartoon-style outputs using OpenCV.
The system must include:

Streamlit frontend for user interaction and visualization

FastAPI backend for authentication, processing, and database operations

PostgreSQL database for user & transaction management

Secure payments (Razorpay/Stripe) before image download

Modular, scalable architecture suitable for industry deployment

The application transforms real-world images into effects such as:

Cartoon Effect

Pencil Sketch

Color Pencil/Artistic Stylization

Advanced Edge+Color Fusion Methods

Users can view a side-by-side comparison of Original vs Transformed Image, and download only after successful payment.

2. Core Outcomes

A robust backend API handling auth, image jobs, payment validation, and file storage.

A Streamlit-based interactive UI with friendly workflow for uploading, previewing, and transforming images.

A highly optimized OpenCV cartoonization pipeline supporting multiple styles.

A secure user login/registration system with JWT authentication.

A payment-locked download system where image access is given only after verified payment.

Fully documented, testable, maintainable code following industry standards.

3. High-Level Architecture (Text Description)
Frontend – Streamlit

User authentication UI (login, signup, forgot password)

Image upload & preview

Style selection

Display cartoon results + side-by-side comparison

Initiate and verify payment

Allow download after backend approval

Backend – FastAPI

Auth routes (JWT-based)

Image processing API

Asynchronous processing pipeline

Endpoints for uploading, transforming, and retrieving image jobs

Payment verification endpoint

PostgreSQL queries using SQLAlchemy

Error & exception handling

Database – PostgreSQL

users table

image_jobs table

payments table

audit_logs (optional future enhancement)

Full referential integrity + indexing

Image Storage

Local storage or S3-compatible bucket for uploaded & processed images

Access via signed URLs

4. Detailed Project Modules
Module 1: User Authentication & Registration (Week 1–2)

Secure user registration with hashed passwords

JWT-based login, refresh tokens

Validation for email format, password strength

Database schema for user accounts

Rate-limiting & brute-force protection

Proper error messages & UX optimization

Module 2: Image Processing with OpenCV (Week 3–4)

Implement a cartoonization engine with:

Techniques

Bilateral Filtering

Edge Detection (Canny or Adaptive Thresholding)

Color Quantization (K-means or manual binning)

Blend edges + quantized colors

Pencil Sketch (grayscale inversion + Gaussian blur + dodge blend)

Color Pencil (stylization + enhanced edges)

Pipeline Requirements

Handle large images efficiently

Output high-resolution processed images

3–5 preset cartoon styles

Side-by-side comparison generation

Allow download preview but restrict final download until payment

Module 3: UI Development & Payment Integration (Week 5–6)
Frontend

Minimalist theme, fast UX

Drag-and-drop upload

Real-time preview

Loading indicators during processing

Responsive layout

Payment Workflow

User uploads → selects style → sees preview

Click on Download → payment gateway opens

Backend validates payment

If valid → generate signed URL → allow download

Backends Supported

Razorpay

Stripe

Module 4: Testing, Review & Documentation (Week 7–8)
Testing

Unit tests for backend endpoints

Integration tests for OpenCV pipeline

UI validation tests

Payment verification mock tests

Load testing for image processing

Documentation

API documentation (OpenAPI Auto-generation)

Developer documentation detailing pipeline logic

Instructions for setup, testing, environment variables

Future roadmap & scalability notes

5. Tech Stack (Finalized)
Frontend

Streamlit

Streamlit Components (for image previews & comparison slider)

Backend

FastAPI

Pydantic

SQLAlchemy

Passlib (password hashing)

JWT Authentication

Image Processing

OpenCV

NumPy

Database

PostgreSQL

Alembic (migrations)

Payments

Razorpay or Stripe SDK

Cloud/Storage

Local FS (development)

AWS S3 / DigitalOcean Spaces (production-ready structure)

6. Project Folder Structure (Industry Standard)
project-root/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routers/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── core/ (auth, security, settings)
│   │   ├── utils/
│   │   ├── image_processing/
│   │   └── payments/
│   ├── migrations/
│   └── requirements.txt
│
├── frontend/
│   ├── streamlit_app.py
│   ├── components/
│   └── assets/
│
├── storage/
│   ├── uploads/
│   ├── processed/
│
├── docs/
└── README.md

7. API Endpoints Overview
Auth

POST /auth/signup

POST /auth/login

GET /auth/me

Images

POST /images/upload

POST /images/process

GET /images/{job_id}

GET /images/download/{job_id} (payment required)

Payments

POST /payments/create-order

POST /payments/verify

8. Deployment (Without Docker/CI/CD for Now)

Include instructions for:

Running backend using Uvicorn

Running Streamlit frontend

Connecting to local/Postgres cloud DB

Setting environment variables

Production settings best practices