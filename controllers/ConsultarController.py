from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from entities.Schemas import ProdutoOut
from repository.ConsultarRepository import listar_produtos

router = APIRouter(prefix="/api", tags=["Produtos"])

# Rota GET /api/produtos que retorna uma lista de ProdutoOut
@router.get("/profutos", response_model = list[ProdutoOut])
def buscar_produtos(
        ordem: Optional[str] = None,
        limit: Optional[int] = None,
        db: Session = Depends(get_db)
):
    # Chama o repositorio passando os parâmetros recebidos na URL
    return listar_produtos(db = db, ordem = ordem, limit = limit)