from fastapi import APIRouter

from database import DbSession
from entities.SaldoModel import SaldoModel
from entities.Schemas import SaldoOut, SaldoUpdate
from repository.SaldoRepository import aplicar_renovacoes, resetar_e_salvar_saldo

router = APIRouter(prefix="/api", tags=["Financeiro"])

@router.get("/saldo", response_model=SaldoOut)
def consultar_saldo(db: DbSession) -> SaldoModel:
    return aplicar_renovacoes(db)


@router.put("/saldo", response_model=SaldoOut)
def atualizar_saldo(dados: SaldoUpdate, db: DbSession) -> SaldoModel:
    # quando fizer o PUT para atualizar o saldo,
    # ele vai primeiro zerar tudo e depois gravar o novo valor
    return resetar_e_salvar_saldo(db, dados.saldo_mensal)