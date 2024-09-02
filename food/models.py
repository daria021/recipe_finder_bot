from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Food(Base):
    __tablename__ = "food"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str]
    price: Mapped[float]
