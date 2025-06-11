"""
Main entry point for the Car Park Availability Finder API.
Creates FastAPI app, registers middlewares, rate-limiter and routes.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from api.routes import router as carpark_router  # your API endpoints


from utils.rate_limit import limiter

# --------------------------------------------------------------------------- #
# Environment
# --------------------------------------------------------------------------- #

load_dotenv()  # read .env (contains VALID_API_KEYS etc.)

# --------------------------------------------------------------------------- #
# FastAPI application
# --------------------------------------------------------------------------- #

app = FastAPI(
    title="NSW Car Park Availability Finder",
    version="1.0.0",
    description="REST API for real-time NSW car-park occupancy and search."
)

# store limiter on app for @limiter.limit decorators in routes.py
app.state.limiter = limiter

# Register SlowAPI rate-limit middleware & 429 handler
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS (open for demo; restrict origins in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------------------------------- #
# Routers
# --------------------------------------------------------------------------- #

app.include_router(carpark_router, prefix="/carparks")
