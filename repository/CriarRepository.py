from sqlalchemy.orm import Session

from entities.ProdutoModel import ProdutoModel
from entities.Schemas import ProdutoIn


def salvar_no_banco(db: Session, item: ProdutoIn) -> ProdutoModel:
    produto = ProdutoModel(
        nome=item.nome,
        categoria=item.categoria.value,
        quantidade=item.quantidade,
        preco_unitario=item.preco_unitario,
    )
    db.add(produto)
    db.commit()
    db.refresh(produto)
    return produto
