from fastapi import APIRouter, HTTPException, status

from database import DbSession
from entities.ProdutoModel import ProdutoModel
from entities.Schemas import ProdutoIn, ProdutoOut, ProdutoUpdate
from repository.EditarRepository import atualizar_produto

router = APIRouter(prefix="/api/produtos", tags=["Produtos"])

def _ou_404(produto: ProdutoModel | None, produto_id: int) -> ProdutoModel:
    if produto is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Produto com ID {produto_id} não foi encontrado.")
    return produto

@router.put("/{produto_id}", response_model=ProdutoOut)
def editar_produto(produto_id: int, dados: ProdutoIn, db: DbSession) -> ProdutoModel:
    """Substitui todos os campos do produto."""
    return _ou_404(atualizar_produto(db=db, produto_id=produto_id, dados=dados), produto_id)


@router.patch("/{produto_id}", response_model=ProdutoOut)
def editar_produto_parcial(produto_id: int, dados: ProdutoUpdate, db: DbSession) -> ProdutoModel:
    """Altera só os campos enviados."""
    return _ou_404(atualizar_produto(db=db, produto_id=produto_id, dados=dados), produto_id)
