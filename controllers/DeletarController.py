from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Importamos a dependencia para obter a conexao com o banco de dados
from database import get_db

# Importamos o Schema de reposta
from entities.Schemas import ProdutoOut

# Importamos a funcao de deleçao do repositorio
from repository.DeletarRepository import deletar_produto

# Criamos o router com o prefixo /api exigido
router = APIRouter(prefix = "/api", tags = ["Produtos"])

# Rota DELETE /api/produtos/{produto_id} para remover um produto
@router.delete("/produtos/{produto_id}", response_model = ProdutoOut)
def remover_produto(produto_id: int, db: Session = Depends(get_db)):
    # 1. Chama o repositorio para tentar encontrar e deletar o produto
    produto_deletado = deletar_produto(db = db, produto_id = produto_id)

    # 2. Se a funcao retornar None, significa que o produto nao existe
    if not produto_deletado:
        # Lança o erro HTTP 404 padronizado no formato {"message": "..."}
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Produto não encontrado."
        )
        # 3. Retorna os dados do produto que acabou de ser removido
    return produto_deletado