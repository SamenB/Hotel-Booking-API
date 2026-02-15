from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base
from sqlalchemy import String, BigInteger

if TYPE_CHECKING:
    from src.models.rooms import RoomsOrm


class FacilitiesOrm(Base):
    __tablename__ = "facilities"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str] = mapped_column(String(100), unique=True)

    rooms: Mapped[list["RoomsOrm"]] = relationship(
        secondary="room_facilities", back_populates="facilities"
    )


# m2m table
class RoomFacilitiesOrm(Base):
    __tablename__ = "room_facilities"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    room_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("rooms.id"))
    facility_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("facilities.id"))
