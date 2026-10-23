from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from entities.SaldoModel import SALDO_ID, SaldoModel
from entities.tempo import agora_utc


def obter_ou_criar_saldo(db: Session) -> SaldoModel:
    """Devolve a linha única do saldo, criando-a (com 0) se ainda não existir."""
    saldo = db.get(SaldoModel, SALDO_ID)
    if saldo is not None:
        return saldo
    try:
        saldo = SaldoModel(id=SALDO_ID, saldo_mensal=Decimal("0"))
        db.add(saldo)
        db.commit()
    except IntegrityError:
        # Outra requisição criou a linha ao mesmo tempo: basta ler a que já existe.
        db.rollback()
        existente = db.get(SaldoModel, SALDO_ID)
        if existente is None:
            raise
        return existente
    db.refresh(saldo)
    return saldo


def salvar_saldo(db: Session, valor: Decimal) -> SaldoModel:
    saldo = obter_ou_criar_saldo(db)
    saldo.saldo_mensal = valor
    saldo.data_saldo = agora_utc()
    db.commit()
    db.refresh(saldo)
    return saldo
