from sqlalchemy.orm import Session

from entities.ProdutoModel import ProdutoModel
from entities.Schemas import Categoria, ProdutoIn, ProdutoUpdate
from repository.SaldoRepository import aplicar_renovacoes, custo_do_item, descontar_do_saldo


def atualizar_produto(db: Session, produto_id: int, dados: ProdutoIn | ProdutoUpdate) -> ProdutoModel | None:
    produto = db.get(ProdutoModel, produto_id)
    if produto is None:
        return None

    aplicar_renovacoes(db)
    custo_antes = custo_do_item(produto.quantidade, produto.preco_unitario)

    # exclude_unset: no PATCH só mudam os campos que vieram no corpo; no PUT vêm todos.
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        if isinstance(valor, Categoria):
            valor = valor.value
        setattr(produto, campo, valor)

    # Se o item ficou mais caro, a diferença sai do saldo. Se ficou mais barato, nada volta.
    custo_depois = custo_do_item(produto.quantidade, produto.preco_unitario)
    descontar_do_saldo(db, custo_depois - custo_antes)

    db.commit()
    db.refresh(produto)
    return produto
