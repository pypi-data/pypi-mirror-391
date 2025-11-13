# models.py
from pydantic import BaseModel
from typing import List, Optional

class ProductItem(BaseModel):
    product_name: str
    brand: str = ""
    specification: str = ""
    main_effect: str  # required

class UserPreferences(BaseModel):
    price_preference: Optional[str] = None  # "cheapest", "balanced", "premium"
    date_preference: Optional[str] = None   # "recent", "any"

class ProductSearchInput(BaseModel):
    product_list: List[ProductItem]
    user_preferences: Optional[UserPreferences] = None