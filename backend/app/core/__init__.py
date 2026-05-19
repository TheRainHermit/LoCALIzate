"""
Core module for LoCALIzate / CaliGuia Backend
==============================================

This module contains the core configuration, database connection,
dependencies, and exception handling for the entire application.

Exports:
    - settings: Application configuration settings
    - get_db: Database client dependency
    - get_current_user: Authentication dependency
    - AppException: Base exception class
    - handle_exception: Global exception handler
"""

from app.core.config import settings
from app.core.database import get_db, init_db
from app.database.supabase_client import supabase_client
from app.core.dependencies import get_current_user, get_current_user_optional, get_supabase_client
from app.core.exceptions import (
    AppException,
    NotFoundException,
    UnauthorizedException,
    ForbiddenException,
    ValidationException,
    ConflictException,
    RateLimitException,
    handle_exception
)

__all__ = [
    # Config
    "settings",
    
    # Database
    "get_db",
    "init_db",
    "supabase_client",
    
    # Dependencies
    "get_current_user",
    "get_current_user_optional",
    "get_supabase_client",
    
    # Exceptions
    "AppException",
    "NotFoundException",
    "UnauthorizedException",
    "ForbiddenException",
    "ValidationException",
    "ConflictException",
    "RateLimitException",
    "handle_exception",
]

__version__ = "1.0.0"
__author__ = "LoCALIzate / CaliGuia Team"
__description__ = "Core module for LoCALIzate Intelligent Tourist Guide"