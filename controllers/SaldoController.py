from fastapi import APIRouter

from database import DbSession
from entities.SaldoModel import SaldoModel
from entities.Schemas import SaldoOut, SaldoUpdate
from repository.SaldoRepository import aplicar_renovacoes, salvar_saldo

router = APIRouter(prefix="/api", tags=["Financeiro"])

@router.get("/saldo", response_model=SaldoOut)
def consultar_saldo(db: DbSession) -> SaldoModel:
    return aplicar_renovacoes(db)


@router.put("/saldo", response_model=SaldoOut)
def atualizar_saldo(dados: SaldoUpdate, db: DbSession) -> SaldoModel:
    return salvar_saldo(db, dados.saldo_mensal)
