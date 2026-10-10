from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from entities.Schemas import ProdutoOut, ProdutoIn
from repository.EditarRepository import atualizar_produto

# Cria o roteador das rotas com o prefixo '/api/produtos'
router = APIRouter(prefix = "/api/produtos", tags = ["Produtos"])

# Rota PUT para atualizar um produto existente pelo ID (ex: put /api/produtos/1)
@router.put("/{produto_id}", response_model = ProdutoOut)
def editar_produto(
        produto_id: int,                    # ID do produto capturado pela URL
        dados: ProdutoIn,               # Corpo da requisicao validado pelo Pydantic
        db: Session = Depends(get_db)       # Injecao de dependencia da sessao com o banco de dados
):
    # 1. Chama a funcao do Repository para atualizar
    produto_atualizado = atualizar_produto(db = db, produto_id = produto_id, dados_atualizacao = dados)

    # 2. Se a funcao retornar None, lanca erro 404
    if not produto_atualizado:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"Produto com ID {produto_id} não foi encontrado."
        )

    # 3. Se tudo correr bem, retorna o produto atualizado ( que é formatado automaticamente pelo Pydantic como ProdutoOut)
    return produto_atualizado