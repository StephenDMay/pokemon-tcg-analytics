from pydantic import BaseModel
from typing import List, Optional

class Card(BaseModel):
    id: str
    name: str
    supertype: str
    subtypes: List[str]
    hp: Optional[str] = None  # Like nullable properties
    types: Optional[List[str]] = None
    evolves_from: Optional[str] = None
    rules: Optional[List[str]] = None
    
    
class Tournament(BaseModel):
    """
    Represents a tournament event.
    Similar to Tournament class in .NET
    """
    id: str
    name: str
    date: datetime
    format: str
    player_count: int
    rounds: int
    status: str

class DeckList(BaseModel):
    """
    Represents a player's deck list.
    Similar to DeckList class in .NET
    """
    id: str
    player_name: str
    placement: int
    points: int
    cards: Dict[str, int]  # Card ID to quantity mapping
    tournament_id: str

    class Config:
        from_attributes = True