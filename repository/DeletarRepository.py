from sqlalchemy.orm import Session

from entities.ProdutoModel import ProdutoModel


def deletar_produto(db: Session, produto_id: int) -> ProdutoModel | None:
    produto = db.get(ProdutoModel, produto_id)
    if produto is None:
        return None
    db.delete(produto)
    db.commit()
    return produto
