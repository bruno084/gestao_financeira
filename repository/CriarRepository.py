from sqlalchemy.orm import Session

from entities.ProdutoModel import ProdutoModel
from entities.Schemas import ProdutoIn
from repository.SaldoRepository import aplicar_renovacoes, custo_do_item, descontar_do_saldo


def salvar_no_banco(db: Session, item: ProdutoIn) -> ProdutoModel:
    aplicar_renovacoes(db)  # soma os meses que já passaram antes de descontar o novo item

    produto = ProdutoModel(
        nome=item.nome,
        categoria=item.categoria.value,
        quantidade=item.quantidade,
        preco_unitario=item.preco_unitario,
    )
    db.add(produto)
    # O item e o desconto no saldo são confirmados juntos: se um falhar, nenhum dos dois vale.
    descontar_do_saldo(db, custo_do_item(item.quantidade, item.preco_unitario))
    db.commit()
    db.refresh(produto)
    return produto
