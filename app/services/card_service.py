from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import HTTPException
from pokemontcgsdk import Card as TCGCard
from pokemontcgsdk import Set as TCGSet
from pokemontcgsdk import RestClient
from app.models.card import Card
from app.core.config import settings
from pokemontcgsdk.restclient import PokemonTcgException

class CardService:
    """
    Service for managing Pokemon card data, handling both TCG SDK interactions
    and local database operations.
    """
    def __init__(self):
        # Initialize the SDK with our API key
        RestClient.configure(settings.POKEMON_TCG_API_KEY)
        # Cache for standard legal sets to reduce API calls
        self._standard_sets_cache: Optional[List[str]] = None
        self._cache_timestamp: Optional[datetime] = None
        self._cache_duration = timedelta(hours=24)

    async def get_card_by_id(self, card_id: str) -> Card:
        """
        Retrieve a card by its ID. First checks local DB (future implementation),
        then falls back to TCG API if not found.
        """
        try:
            tcg_card = await self._run_sync(lambda: TCGCard.find(card_id))
            if not tcg_card:
                raise HTTPException(status_code=404, detail="Card not found")
            return Card.convert_from_tcg_card(tcg_card)
        except PokemonTcgException as e:
            # Properly decode the error message from bytes
            error_message = e.args[0].decode('utf-8') if isinstance(e.args[0], bytes) else str(e)
            raise HTTPException(status_code=404, detail=error_message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def _run_sync(self, func):
        """
        Helper method to run synchronous SDK calls in an async context.
        """
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func)

    async def get_standard_legal_cards(self) -> List[Card]:
        """
        Retrieve all standard legal cards.
        """
        try:
            # Wrap the synchronous SDK call in _run_sync
            tcg_cards = await self._run_sync(
                lambda: TCGCard.where(q='legalities.standard:legal')
            )
            return Card.convert_from_tcg_cards(tcg_cards)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching standard cards: {str(e)}")

    async def get_standard_sets(self) -> List[str]:
        """
        Get all standard legal set IDs with caching.
        """
        if (
            self._standard_sets_cache is not None 
            and self._cache_timestamp is not None
            and datetime.now() - self._cache_timestamp < self._cache_duration
        ):
            return self._standard_sets_cache

        try:
            standard_sets = await self._run_sync(
                lambda: TCGSet.where(q='legalities.standard:legal')
            )
            self._standard_sets_cache = [set_obj.id for set_obj in standard_sets]
            self._cache_timestamp = datetime.now()
            return self._standard_sets_cache
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching standard sets: {str(e)}")

    async def get_cards_by_set(self, set_id: str) -> List[Card]:
        """
        Retrieve all cards from a specific set.
        """
        try:
            tcg_cards = await self._run_sync(
                lambda: TCGCard.where(q=f'set.id:{set_id}')
            )
            return Card.convert_from_tcg_cards(tcg_cards)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching cards from set {set_id}: {str(e)}")

    async def sync_standard_cards(self) -> Dict[str, Any]:
        """
        Synchronize all standard legal cards with local database.
        Returns statistics about the sync operation.
        """
        stats = {
            "total_cards_processed": 0,
            "new_cards_added": 0,
            "cards_updated": 0,
            "errors": []
        }

        try:
            # Get all standard sets
            standard_sets = await self.get_standard_sets()
            
            # Process each set
            for set_id in standard_sets:
                try:
                    # Get all cards in the set
                    cards = await self.get_cards_by_set(set_id)
                    stats["total_cards_processed"] += len(cards)
                    
                    for card in cards:
                        if card.is_standard_legal():
                            # TODO: Once DB is implemented:
                            # 1. Check if card exists in DB
                            # 2. If exists, update if needed and increment cards_updated
                            # 3. If doesn't exist, insert and increment new_cards_added
                            stats["new_cards_added"] += 1  # Temporary placeholder
                            
                except Exception as e:
                    stats["errors"].append(f"Error processing set {set_id}: {str(e)}")
                    continue
                    
            return stats
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error during standard cards synchronization: {str(e)}"
            )

    async def search_cards(
        self,
        name: Optional[str] = None,
        type: Optional[str] = None,
        supertype: Optional[str] = None,
        rarity: Optional[str] = None,
        set_name: Optional[str] = None,
        standard_legal: bool = True
    ) -> List[Card]:
        """
        Search for cards based on various criteria.
        All parameters are optional and can be combined.
        """
        try:
            # Build the query string
            query_parts = []
            
            if standard_legal:
                query_parts.append('legalities.standard:legal')
            if name:
                query_parts.append(f'name:{name}*')  # Using wildcard for partial matches
            if type:
                query_parts.append(f'types:{type}')
            if supertype:
                query_parts.append(f'supertype:{supertype}')
            if rarity:
                query_parts.append(f'rarity:{rarity}')
            if set_name:
                query_parts.append(f'set.name:{set_name}')
                
            query = ' '.join(query_parts)
            
            tcg_cards = await self._run_sync(lambda: TCGCard.where(q=query))
            return Card.convert_from_tcg_cards(tcg_cards)
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error searching cards: {str(e)}"
            )

    async def get_card_price_history(self, card_id: str) -> Dict[str, Any]:
        """
        Get price history for a specific card.
        This is a placeholder for future implementation when we have our own DB
        tracking price history.
        """
        # TODO: Implement once we have DB set up to track price history
        try:
            card = await self.get_card_by_id(card_id)
            if card and card.tcgplayer:
                return {
                    "card_id": card_id,
                    "current_prices": card.tcgplayer.prices,
                    "last_updated": card.tcgplayer.updatedAt,
                    # Future: Will include historical price data from our DB
                }
            return {}
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching price history: {str(e)}"
            )