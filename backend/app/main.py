"""
Main FastAPI application entry point.
Handles app factory, router registration, middleware, and CORS configuration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.db import init_db
from app.routers import auth, images, payments, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events."""
    # Startup
    await init_db()
    yield
    # Shutdown
    pass


def create_app() -> FastAPI:
    """Application factory function."""
    app = FastAPI(
        title="AI Image Transformation API",
        description="Transform images into cartoon-style effects using OpenCV",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
    app.include_router(users.router, prefix="/users", tags=["Users"])
    app.include_router(images.router, prefix="/images", tags=["Images"])
    app.include_router(payments.router, prefix="/payments", tags=["Payments"])

    @app.get("/", tags=["Health"])
    async def root():
        """Health check endpoint."""
        return {"status": "healthy", "message": "AI Image Transformation API"}

    return app


app = create_app()
