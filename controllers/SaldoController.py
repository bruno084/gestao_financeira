from fastapi import APIRouter

from database import DbSession
from entities.SaldoModel import SaldoModel
from entities.Schemas import SaldoOut, SaldoUpdate
from repository.SaldoRepository import obter_ou_criar_saldo, salvar_saldo

router = APIRouter(prefix="/api", tags=["Financeiro"])

@router.get("/saldo", response_model=SaldoOut)
def consultar_saldo(db: DbSession) -> SaldoModel:
    return obter_ou_criar_saldo(db)

@router.put("/saldo", response_model=SaldoOut)
def atualizar_saldo(dados: SaldoUpdate, db: DbSession) -> SaldoModel:
    return salvar_saldo(db, dados.saldo_mensal)
