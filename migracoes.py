"""Ajusta bancos criados por versões antigas (o SQLite não adiciona colunas sozinho)."""
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import Engine, inspect, text

from service import Renovacao

_CENTAVOS = Decimal("0.01")


def migrar(engine: Engine) -> None:
    """Acrescenta as colunas de saldo disponível na tabela 'saldo' e preenche com o que a tela mostrava."""
    inspetor = inspect(engine)
    if "saldo" not in inspetor.get_table_names():
        return
    if "saldo_disponivel" in {coluna["name"] for coluna in inspetor.get_columns("saldo")}:
        return  # banco já está atualizado

    with engine.begin() as conexao:  # uma transação só: ou migra tudo ou nada
        conexao.execute(text("ALTER TABLE saldo ADD COLUMN saldo_disponivel NUMERIC(12, 2) NOT NULL DEFAULT 0"))
        conexao.execute(text("ALTER TABLE saldo ADD COLUMN total_creditado NUMERIC(12, 2) NOT NULL DEFAULT 0"))
        conexao.execute(text("ALTER TABLE saldo ADD COLUMN renovacoes_aplicadas INTEGER NOT NULL DEFAULT 0"))

        linha = conexao.execute(text("SELECT saldo_mensal, data_saldo FROM saldo WHERE id = 1")).one_or_none()
        if linha is None or linha.data_saldo is None:
            return

        mensal = Decimal(str(linha.saldo_mensal))
        renovacoes = Renovacao.renovacoes_ate(
            Renovacao.data_em_brasilia(datetime.fromisoformat(str(linha.data_saldo))), Renovacao.hoje_em_brasilia()
        )
        gasto_atual = Decimal(str(conexao.execute(
            text("SELECT COALESCE(SUM(quantidade * preco_unitario), 0) FROM produtos")
        ).scalar_one()))

        creditado = (mensal * (1 + renovacoes)).quantize(_CENTAVOS, rounding=ROUND_HALF_UP)
        disponivel = (creditado - gasto_atual).quantize(_CENTAVOS, rounding=ROUND_HALF_UP)
        conexao.execute(
            text("UPDATE saldo SET total_creditado = :c, saldo_disponivel = :d, renovacoes_aplicadas = :r WHERE id = 1"),
            {"c": float(creditado), "d": float(disponivel), "r": renovacoes},
        )
