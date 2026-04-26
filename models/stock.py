#table postgresql

from sqlalchemy import Integer, Column, String, DateTime, Date, Float, BigInteger, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class Stock(Base):
    __tablename__ = 'stock'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticker: Mapped[str] = mapped_column(String, nullable=False, index=True)
    date: Mapped[Date] = mapped_column(Date, nullable=False)
    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[float] = mapped_column(BigInteger, nullable=False)

    __table_args__ = (UniqueConstraint("ticker", "date"),)


