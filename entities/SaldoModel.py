"""Tabela 'saldo': guarda uma única linha (id fixo) com o saldo mensal."""
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from database import Base

SALDO_ID = 1


class SaldoModel(Base):
    __tablename__ = "saldo"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    saldo_mensal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0"))
    data_saldo: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
