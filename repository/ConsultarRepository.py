from typing import Literal

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from entities.ProdutoModel import ProdutoModel


def _escapar_like(texto: str) -> str:
    """Impede que % e _ digitados pelo usuário virem curingas da busca."""
    return texto.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def listar_produtos(
    db: Session,
    ordem: Literal["recentes"] | None = None,
    limit: int | None = None,
    busca: str | None = None,
) -> list[ProdutoModel]:
    stmt = select(ProdutoModel)

    if busca:
        stmt = stmt.where(ProdutoModel.nome.ilike(f"%{_escapar_like(busca)}%", escape="\\"))

    # O id entra como desempate: dois itens criados no mesmo instante mantêm ordem estável.
    if ordem == "recentes":
        stmt = stmt.order_by(desc(ProdutoModel.criado_em), desc(ProdutoModel.id))
    else:
        stmt = stmt.order_by(ProdutoModel.id)

    if limit is not None:
        stmt = stmt.limit(limit)

    return list(db.scalars(stmt).all())
