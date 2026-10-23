from fastapi import APIRouter

from database import DbSession
from entities.Schemas import ResumoFinanceiro
from service.FinanceiroService import FinanceiroService

router = APIRouter(prefix="/api/financeiro", tags=["Financeiro"])

@router.get("/resumo", response_model=ResumoFinanceiro)
def resumo_financeiro(db: DbSession) -> ResumoFinanceiro:
    return FinanceiroService.montar_resumo(db)
