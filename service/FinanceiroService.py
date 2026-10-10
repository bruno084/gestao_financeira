from sqlalchemy.orm import Session
from entities.ProdutoModel import ProdutoModel

def calcular_resumo_financeiro(db: Session):
    # 1. Procura todos os produtos registrados no banco
    produtos = db.query(ProdutoModel).all()

    # . Calcula a quantidade total de itens somando o stock de cada produto
    total_itens = sum(p.quantidade for p in produtos)

    # 3. Calcula o valor financeiro total do stock (quantidade * preco unitario de cada item)
    valor_total_estoque = sum(p.quantidade * p.preco_unitario for p in produtos)

    # 4. Retorna um dicionario estruturado com os dados consolidados o inventario
    return {
        "totalProdutos": len(produtos),             # Quantidade de produtos diferentes registrados
        "totalItemsEmEstoque": total_itens,         # Soma total das quantidades fisicas em stock
        "valorTotalEstoque": valor_total_estoque    # Soma total do valor em dinheiro parado no stock
    }
