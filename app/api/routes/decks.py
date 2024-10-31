# Similar to CardsController.cs in ASP.NET Core
# Defines API routes and handlers for deck-related operations
from fastapi import APIRouter, Depends, HTTPException
from app.services.limitless_service import LimitlessService
from app.models.schemas import DeckList

router = APIRouter()

@router.get("/{deck_id}", response_model=DeckList)
async def get_deck(
    deck_id: str,
    service: LimitlessService = Depends(LimitlessService)
):
    deck = await service.get_deckList(deck_id)
    if not deck:
        raise HTTPException(status_code=404, detail="Card not found")
    return deck