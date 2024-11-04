# app/models/card.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from pokemontcgsdk import Card as TCGCard

class Ability(BaseModel):
    name: str
    text: str
    type: Optional[str] = None

class Attack(BaseModel):
    name: str
    cost: List[str]
    convertedEnergyCost: int
    damage: Optional[str] = None
    text: Optional[str] = None

class Effect(BaseModel):
    type: str
    value: str

class Price(BaseModel):
    low: Optional[float] = None
    mid: Optional[float] = None
    high: Optional[float] = None
    market: Optional[float] = None
    directLow: Optional[float] = None

class CardSet(BaseModel):
    id: str
    name: str
    series: str
    printedTotal: int
    total: int
    legalities: Dict[str, Optional[str]]  
    ptcgoCode: Optional[str] = None
    releaseDate: str
    updatedAt: str

class CardImages(BaseModel):
    small: str
    large: str

class TCGPlayer(BaseModel):
    url: str
    updatedAt: str
    prices: Dict[str, Optional[Price]] = Field(default_factory=dict)  

class Card(BaseModel):
    # Required fields
    id: str
    name: str
    supertype: str
    subtypes: List[str]
    number: str
    images: CardImages
    set: CardSet
    
    # Optional fields with defaults
    level: Optional[str] = None
    hp: Optional[str] = None
    types: Optional[List[str]] = None
    evolvesFrom: Optional[str] = None
    evolvesTo: Optional[List[str]] = Field(default_factory=list)
    rules: Optional[List[str]] = Field(default_factory=list)
    abilities: Optional[List[Ability]] = Field(default_factory=list)
    attacks: Optional[List[Attack]] = Field(default_factory=list)
    weaknesses: Optional[List[Effect]] = Field(default_factory=list)
    resistances: Optional[List[Effect]] = Field(default_factory=list)
    retreatCost: Optional[List[str]] = Field(default_factory=list)
    rarity: Optional[str] = None
    legalities: Dict[str, Optional[str]] = Field(default_factory=dict)  # Changed to allow None values
    regulationMark: Optional[str] = None
    tcgplayer: Optional[TCGPlayer] = None
    
    # Metadata fields
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_synced_at: datetime = Field(default_factory=datetime.now)

    @staticmethod
    def _convert_to_dict(obj: Any) -> Any:
        """Helper method to convert objects to dictionaries recursively"""
        if hasattr(obj, '__dict__'):
            return {k: Card._convert_to_dict(v) for k, v in obj.__dict__.items() 
                   if not k.startswith('_')}
        elif isinstance(obj, (list, tuple)):
            return [Card._convert_to_dict(x) for x in obj]
        elif isinstance(obj, dict):
            return {k: Card._convert_to_dict(v) for k, v in obj.items()}
        return obj

    @classmethod
    def convert_from_tcg_card(cls, tcg_card: Union[TCGCard, Dict[str, Any]]) -> "Card":
        """Create internal Card model from TCG SDK card"""
        if isinstance(tcg_card, TCGCard):
            # Convert the entire TCG card object to a dictionary
            card_dict = cls._convert_to_dict(tcg_card)
            
            # Ensure required fields have default values if missing
            card_dict.setdefault('evolvesTo', [])
            card_dict.setdefault('rules', [])
            card_dict.setdefault('abilities', [])
            card_dict.setdefault('attacks', [])
            card_dict.setdefault('weaknesses', [])
            card_dict.setdefault('resistances', [])
            card_dict.setdefault('retreatCost', [])
            
            # Handle legalities
            if 'legalities' in card_dict:
                card_dict['legalities'] = {
                    k: v if v is not None else 'None'
                    for k, v in card_dict['legalities'].items()
                }
            
            if 'set' in card_dict and 'legalities' in card_dict['set']:
                card_dict['set']['legalities'] = {
                    k: v if v is not None else 'None'
                    for k, v in card_dict['set']['legalities'].items()
                }
            
            # Handle TCGPlayer prices
            if 'tcgplayer' in card_dict and card_dict['tcgplayer']:
                tcgplayer_dict = card_dict['tcgplayer']
                if 'prices' in tcgplayer_dict:
                    prices_dict = {}
                    for price_key, price_obj in tcgplayer_dict['prices'].items():
                        if price_obj is not None:
                            prices_dict[price_key] = cls._convert_to_dict(price_obj)
                        else:
                            prices_dict[price_key] = None
                    tcgplayer_dict['prices'] = prices_dict
                card_dict['tcgplayer'] = tcgplayer_dict

            # Create the Card instance
            return cls(**card_dict)
        else:
            # If we received a dict, use it directly
            return cls(**tcg_card)

    @classmethod
    def convert_from_tcg_cards(cls, tcg_cards: List[Union[TCGCard, Dict[str, Any]]]) -> List["Card"]:
        """Convert a list of TCG cards to internal Card models."""
        return [cls.convert_from_tcg_card(card) for card in tcg_cards]

    def is_standard_legal(self) -> bool:
        """Check if card is legal in Standard format"""
        return self.legalities.get("standard") == "legal"