from fastapi import APIRouter, HTTPException, status

from database import DbSession
from entities.ProdutoModel import ProdutoModel
from entities.Schemas import ProdutoOut
from repository.DeletarRepository import deletar_produto

router = APIRouter(prefix="/api", tags=["Produtos"])


@router.delete("/produtos/{produto_id}", response_model=ProdutoOut)
def remover_produto(produto_id: int, db: DbSession) -> ProdutoModel:
    produto = deletar_produto(db=db, produto_id=produto_id)
    if produto is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Produto não encontrado.")
    return produto
