"""Regras do saldo. Todas as contas são feitas em UPDATEs do próprio banco (atômicos), então duas
requisições ao mesmo tempo não se atropelam."""
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import func, literal, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from entities.SaldoModel import SALDO_ID, SaldoModel
from entities.tempo import agora_utc
from service import Renovacao

_CENTAVOS = Decimal("0.01")


def custo_do_item(quantidade: int, preco_unitario: Decimal) -> Decimal:
    """Quanto um item custa: quantidade x preço unitário, em centavos."""
    return (Decimal(quantidade) * preco_unitario).quantize(_CENTAVOS, rounding=ROUND_HALF_UP)


def obter_ou_criar_saldo(db: Session) -> SaldoModel:
    """Devolve a linha única do saldo, criando-a (zerada) se ainda não existir."""
    saldo = db.get(SaldoModel, SALDO_ID)
    if saldo is not None:
        return saldo
    try:
        saldo = SaldoModel(id=SALDO_ID)
        saldo.saldo_mensal = Decimal("0")
        saldo.saldo_disponivel = Decimal("0")
        saldo.total_creditado = Decimal("0")
        saldo.renovacoes_aplicadas = 0
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


def aplicar_renovacoes(db: Session) -> SaldoModel:
    """Soma ao saldo disponível os meses que já passaram desde o último acesso (sem agendador)."""
    saldo = obter_ou_criar_saldo(db)
    if saldo.data_saldo is None:
        return saldo  # o saldo ainda não foi definido

    devidas = Renovacao.renovacoes_ate(Renovacao.data_em_brasilia(saldo.data_saldo), Renovacao.hoje_em_brasilia())
    pendentes = devidas - saldo.renovacoes_aplicadas
    if pendentes <= 0:
        return saldo

    credito = SaldoModel.saldo_mensal * pendentes
    db.execute(
        update(SaldoModel)
        # O filtro garante que, se outra requisição já somou esses meses, esta não soma de novo.
        .where(SaldoModel.id == SALDO_ID, SaldoModel.renovacoes_aplicadas == saldo.renovacoes_aplicadas)
        .values(
            saldo_disponivel=func.round(SaldoModel.saldo_disponivel + credito, 2),
            total_creditado=func.round(SaldoModel.total_creditado + credito, 2),
            renovacoes_aplicadas=devidas,
        )
    )
    db.commit()
    db.refresh(saldo)
    return saldo


def descontar_do_saldo(db: Session, custo: Decimal) -> None:
    """Tira o custo do saldo disponível. Não confirma a transação: quem chama faz o commit junto com
    a operação do produto, para os dois acontecerem ou nenhum acontecer."""
    if custo <= 0:
        return
    db.execute(
        update(SaldoModel)
        .where(SaldoModel.id == SALDO_ID)
        .values(saldo_disponivel=func.round(SaldoModel.saldo_disponivel - custo, 2))
    )


def salvar_saldo(db: Session, valor: Decimal) -> SaldoModel:
    """Define o saldo mensal. A diferença para o valor anterior é somada (ou tirada) do saldo disponível:
    no primeiro salvamento entra o valor inteiro; trocar 200 por 300 soma 100; trocar 300 por 200 tira 100."""
    saldo = aplicar_renovacoes(db)  # antes de mudar o valor, fecha os meses que já passaram com o valor antigo
    if saldo.data_saldo is not None and saldo.saldo_mensal == valor:
        return saldo

    diferenca = literal(valor) - SaldoModel.saldo_mensal
    db.execute(
        update(SaldoModel)
        .where(SaldoModel.id == SALDO_ID)
        .values(
            saldo_mensal=valor,
            saldo_disponivel=func.round(SaldoModel.saldo_disponivel + diferenca, 2),
            total_creditado=func.round(SaldoModel.total_creditado + diferenca, 2),
            # A data do primeiro salvamento é mantida: ela define o dia da renovação.
            data_saldo=func.coalesce(SaldoModel.data_saldo, agora_utc()),
        )
    )
    db.commit()
    db.refresh(saldo)
    return saldo
