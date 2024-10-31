# Similar to CardsController.cs in ASP.NET Core
# Defines API routes and handlers for card-related operations
from fastapi import APIRouter, Depends, HTTPException
from app.services.pokemon_tcg_service import PokemonTCGService
from app.models.schemas import Card

router = APIRouter()

@router.get("/{card_id}", response_model=Card)
async def get_card(
    card_id: str,
    service: PokemonTCGService = Depends(PokemonTCGService)
):
    card = await service.get_card(card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return card