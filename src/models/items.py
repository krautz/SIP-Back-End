from pydantic import BaseModel


class ItemWithPrice(BaseModel):
    app_id: int
    name: str
    price_unitary: float | None
    amount: int
    api_error: str
    price_date: str
    price_date_timestamp: int
    market_hash_name: str


class Item(BaseModel):
    app_id: int
    name: str
    amount: int
    market_hash_name: str


AnyItem = Item | ItemWithPrice
