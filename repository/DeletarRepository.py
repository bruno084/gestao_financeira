from typing import Optional
from sqlalchemy.orm import Session

# Importamos o modelo ORM da tabela de produtos para poder consultar e remover no SQLite
from entities.ProdutoModel import ProdutoModel


# Função responsavel por procurar e remover um produto pelo seu ID no banco.db
def deletar_produto(db: Session, produto_id: int) -> Optional[ProdutoModel]:
    # 1. Faz uma busca no banco SQLite para encontrar o produto correspondente ao ID
    produto = db.query(ProdutoModel).filter(ProdutoModel.id == produto_id).first()

    # 2. Se o produto nao for encontrado, retorna None (indicando inexistencia)
    if not produto:
        return None

    # 3. Remove o objeto do produto da sessao do banco de dados
    db.delete(produto)

    # 4. Confirma e grava a exclusao permanentemente no arquivo banco.db
    db.commit()

    # 5. Retorna o produto que foi removido (util para o controller confirmar o registro)
    return produto