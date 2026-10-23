from sqlalchemy.orm import Session

from entities.ProdutoModel import ProdutoModel
from entities.Schemas import Categoria, ProdutoIn, ProdutoUpdate


def atualizar_produto(db: Session, produto_id: int, dados: ProdutoIn | ProdutoUpdate) -> ProdutoModel | None:
    produto = db.get(ProdutoModel, produto_id)
    if produto is None:
        return None

    # exclude_unset: no PATCH só mudam os campos que vieram no corpo; no PUT vêm todos.
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        if isinstance(valor, Categoria):
            valor = valor.value
        setattr(produto, campo, valor)

    db.commit()
    db.refresh(produto)
    return produto
