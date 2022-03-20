from db.metadata import Base
from sqlalchemy import Column, Integer, String, Date

class List(Base):
    __bind_key__ = "sip"
    __tablename__ = "list"

    id = Column(Integer, primary_key=True, autoincrement=True)
    steam_id = Column(Integer, primary_key=True)
    name = Column(String(length=100), nullable=False)
    created_at = Column(Date, nullable=False)
    updated_at = Column(Date, nullable=False)
