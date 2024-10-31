# routes/cards.py
# Similar to CardsController.cs in ASP.NET Core
# Defines API routes and handlers for card-related operations
from fastapi import APIRouter, Depends, HTTPException
from app.services.card_service import CardService
from app.models.card import Card
import logging
from pokemontcgsdk.restclient import PokemonTcgException

router = APIRouter()

@router.get("/{card_id}", response_model=Card)
async def get_card(
    card_id: str,
    service: CardService = Depends(CardService)
) -> Card:
    try:
        logging.debug(f'Getting card with ID: {card_id}')
        return await service.get_card_by_id(card_id)
    except PokemonTcgException as e:
        # Handle Pokemon TCG API specific errors
        error_message = e.args[0].decode('utf-8') if isinstance(e.args[0], bytes) else str(e)
        raise HTTPException(status_code=404, detail=f"Card not found: {error_message}")
    except Exception as e:
        # Handle other unexpected errors
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")