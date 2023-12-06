from pydantic import BaseModel, Field


class InventoryAsset(BaseModel):
    class Config:
        populate_by_name = True

    app_id: int = Field(alias="appid")
    context_id: str = Field(alias="contextid")
    asset_id: str = Field(alias="assetid")
    class_id: str = Field(alias="classid")
    instance_id: str = Field(alias="instanceid")
    amount: int


class InventoryDescriptionDescription(BaseModel):
    type: str
    value: str


class InventoryDescriptionAction(BaseModel):
    link: str
    name: str


class InventoryDescriptionTag(BaseModel):
    category: str
    internal_name: str
    localized_category_name: str
    localized_tag_name: str


class InventoryDescription(BaseModel):
    class Config:
        populate_by_name = True

    app_id: int = Field(alias="appid")
    class_id: str = Field(alias="classid")
    instance_id: str = Field(alias="instanceid")
    currency: int
    background_color: str
    icon_url: str
    icon_url_large: str = ""
    descriptions: list[InventoryDescriptionDescription]
    tradable: int
    actions: list[InventoryDescriptionAction] = []
    name: str
    name_color: str
    type: str
    market_name: str
    market_hash_name: str
    market_actions: list[InventoryDescriptionAction] = []
    commodity: int
    market_tradable_restriction: int
    marketable: int
    tags: list[InventoryDescriptionTag]
    fraudwarnings: list[str] = []


class Inventory(BaseModel):
    assets: list[InventoryAsset]
    descriptions: list[InventoryDescription]
    total_inventory_count: int
    success: int
    rwgrsn: int
