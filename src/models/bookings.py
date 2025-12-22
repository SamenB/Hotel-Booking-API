from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.hybrid import hybrid_property
from src.database import Base
from datetime import date
from sqlalchemy import DateTime, Integer, ForeignKey


class BookingsOrm(Base):
    __tablename__ = "bookings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    hotel_id: Mapped[int] = mapped_column(Integer, ForeignKey("hotels.id"))
    room_id: Mapped[int] = mapped_column(Integer, ForeignKey("rooms.id"))
    check_in_date: Mapped[date] = mapped_column(DateTime)
    check_out_date: Mapped[date] = mapped_column(DateTime)
    price: Mapped[int] = mapped_column(Integer)

    @hybrid_property
    def total_price(self) -> int:
        return self.price * (self.check_out_date - self.check_in_date).days
