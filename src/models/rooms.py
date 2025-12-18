from sqlalchemy.orm import Mapped, mapped_column
from src.database import Base
from sqlalchemy import String, BigInteger, ForeignKey


class RoomsORM(Base):
    __tablename__ = "rooms"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    hotel_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("hotels.id"))
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(String(1000000))
    price: Mapped[int]
    quantity: Mapped[int]
