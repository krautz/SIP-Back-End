from db.metadata import Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Float,
    ForeignKey,
)
from sqlalchemy.orm import relationship


class List(Base):
    __bind_key__ = "sip"
    __tablename__ = "list"

    id = Column(Integer, primary_key=True, autoincrement=True)
    steam_id = Column(Integer, primary_key=True)
    name = Column(String(length=100), nullable=False)
    created_at = Column(Date, nullable=False)
    updated_at = Column(Date, nullable=False)

    list_items = relationship("ItemList", back_populates="list", cascade="all, delete-orphan")


class Item(Base):
    __bind_key__ = "sip"
    __tablename__ = "item"

    market_hash_name = Column(String(length=150), primary_key=True)
    app_id = Column(Integer, nullable=False)
    name_pt = Column(String(length=150), nullable=True)
    name_en = Column(String(length=150), nullable=True)

    item_prices = relationship("ItemPrice", back_populates="item", cascade="all, delete-orphan")
    item_lists = relationship("ItemList", back_populates="item", cascade="all, delete-orphan")


    @property
    def id(self):
        return self.market_hash_name


    @property
    def name(self):
        return self.name_en


class ItemPrice(Base):
    __bind_key__ = "sip"
    __tablename__ = "item_price"

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(String(length=150), ForeignKey("item.market_hash_name"), nullable=False)
    date = Column(Date, nullable=False)
    price_usd = Column(Float, nullable=False)

    item = relationship("Item", back_populates="item_prices", uselist=False)


    @property
    def price(self):
        return self.price_usd


class ItemList(Base):
    __bind_key__ = "sip"
    __tablename__ = "item_list"

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(String(length=150), ForeignKey("item.market_hash_name"), nullable=False)
    list_id = Column(Integer, ForeignKey("list.id"), nullable=False)
    quantity = Column(Integer, nullable=False)

    list = relationship("List", back_populates="list_items", uselist=False)
    item = relationship("Item", back_populates="item_lists", uselist=False)
