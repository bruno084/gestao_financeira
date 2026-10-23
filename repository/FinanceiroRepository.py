from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from entities.ProdutoModel import ProdutoModel

_CENTAVOS = Decimal("0.01")


def somar_gastos_por_categoria(db: Session) -> list[tuple[str, Decimal]]:
    """Soma quantidade x preço unitário por categoria direto no banco (sem carregar todos os produtos)."""
    total = func.sum(ProdutoModel.quantidade * ProdutoModel.preco_unitario)
    linhas = db.execute(select(ProdutoModel.categoria, total).group_by(ProdutoModel.categoria)).all()
    return [
        (categoria, Decimal(str(soma or 0)).quantize(_CENTAVOS, rounding=ROUND_HALF_UP))
        for categoria, soma in linhas
    ]
