from fastapi import APIRouter

from database import DbSession
from entities.ProdutoModel import ProdutoModel
from entities.Schemas import ProdutoIn, ProdutoOut
from repository.CriarRepository import salvar_no_banco

router = APIRouter(prefix="/api", tags=["Produtos"])


@router.post("/produtos", response_model=ProdutoOut, status_code=201)
def criar_produto(item: ProdutoIn, db: DbSession) -> ProdutoModel:
    return salvar_no_banco(db=db, item=item)
