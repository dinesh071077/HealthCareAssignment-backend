"""
FastAPI Application Entry Point — AI-First CRM Healthcare Professional Module
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import engine, Base
from app.api.routers import chat, interactions, doctors

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI-First CRM — Healthcare Professional Module",
    description="Production-ready CRM for Pharmaceutical Field Representatives powered by LangGraph and Groq.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(chat.router, prefix="/api")
app.include_router(interactions.router, prefix="/api")
app.include_router(doctors.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "AI-First CRM Healthcare API is running 🚀"}


@app.get("/health")
def health():
    return {"status": "ok"}
