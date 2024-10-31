# Similar to CardsController.cs in ASP.NET Core
# Defines API routes and handlers for deck-related operations
from fastapi import APIRouter, Depends, HTTPException
from app.services.limitless_service import LimitlessService


router = APIRouter()
