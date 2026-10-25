"""Tabela 'saldo': guarda uma única linha (id fixo) com o saldo mensal e o saldo disponível."""
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from database import Base

SALDO_ID = 1


class SaldoModel(Base):
    __tablename__ = "saldo"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # Valor fixo que entra todo mês (quanto a pessoa quer gastar por mês com o estoque).
    saldo_mensal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0"))
    # Dia do primeiro salvamento: é o dia do mês em que o saldo mensal é somado de novo.
    data_saldo: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    # O que ainda pode ser usado em itens. Diminui ao cadastrar e nunca é devolvido.
    saldo_disponivel: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0"), server_default="0"
    )
    # Tudo que já entrou (valor mensal x meses). Gasto = total_creditado - saldo_disponivel.
    total_creditado: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0"), server_default="0"
    )
    # Quantas renovações mensais já foram somadas (evita somar o mesmo mês duas vezes).
    renovacoes_aplicadas: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
