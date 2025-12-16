from sqlalchemy.orm import Mapped, mapped_column
from src.database import Base
from sqlalchemy import String, BigInteger


class UsersOrm(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(String(100))
    password: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(200))
