from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Numeric, String, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class IPO(Base):
    __tablename__ = "ipos"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    company_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    symbol: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    lot_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    total_lots: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    open_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    close_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="UPCOMING"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )