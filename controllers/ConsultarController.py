from typing import Annotated, Literal

from fastapi import APIRouter, Query

from database import DbSession
from entities.ProdutoModel import ProdutoModel
from entities.Schemas import ProdutoOut
from repository.ConsultarRepository import listar_produtos

router = APIRouter(prefix="/api", tags=["Produtos"])

@router.get("/produtos", response_model=list[ProdutoOut])
def buscar_produtos(
    db: DbSession,
    ordem: Literal["recentes"] | None = None,
    limit: Annotated[int | None, Query(ge=1, le=1000)] = None,
    busca: Annotated[str | None, Query(max_length=100)] = None,
) -> list[ProdutoModel]:
    return listar_produtos(db=db, ordem=ordem, limit=limit, busca=busca)
