from datetime import timedelta
from decimal import Decimal
from pathlib import Path

from sqlalchemy import create_engine, text

from entities.tempo import agora_utc
from migracoes import migrar
from service import Renovacao


def _banco_antigo(caminho: Path, dias_desde_o_saldo: int):  # type: ignore[no-untyped-def]
    """Cria um banco como o das versões anteriores: tabela saldo sem as colunas novas."""
    engine = create_engine(f"sqlite:///{caminho.as_posix()}")
    with engine.begin() as c:
        c.execute(text("CREATE TABLE produtos (id INTEGER PRIMARY KEY, nome VARCHAR(100), categoria VARCHAR(20), "
                       "quantidade INTEGER, preco_unitario NUMERIC(10,2), criado_em DATETIME)"))
        c.execute(text("CREATE TABLE saldo (id INTEGER PRIMARY KEY, saldo_mensal NUMERIC(12,2) NOT NULL, data_saldo DATETIME)"))
        c.execute(text("INSERT INTO produtos VALUES (1,'Arroz','COMIDA',2,10.5,:d), (2,'Sabao','LIMPEZA',3,4,:d)"),
                  {"d": agora_utc().isoformat(sep=" ")})
        c.execute(text("INSERT INTO saldo VALUES (1, 200, :d)"), {"d": (agora_utc() - timedelta(days=dias_desde_o_saldo)).isoformat(sep=" ")})
    return engine


def _ler(engine) -> tuple[Decimal, Decimal, int]:  # type: ignore[no-untyped-def]
    with engine.connect() as c:
        linha = c.execute(text("SELECT total_creditado, saldo_disponivel, renovacoes_aplicadas FROM saldo")).one()
    return Decimal(str(linha[0])), Decimal(str(linha[1])), int(linha[2])


def test_migra_banco_antigo_preservando_o_que_a_tela_mostrava(tmp_path: Path) -> None:
    engine = _banco_antigo(tmp_path / "antigo.db", dias_desde_o_saldo=70)
    migrar(engine)
    renovacoes = Renovacao.renovacoes_ate(
        Renovacao.data_em_brasilia(agora_utc() - timedelta(days=70)), Renovacao.hoje_em_brasilia()
    )
    creditado = Decimal(200) * (1 + renovacoes)
    assert _ler(engine) == (creditado, creditado - Decimal("33"), renovacoes)  # gasto atual: 21 + 12


def test_migracao_roda_so_uma_vez(tmp_path: Path) -> None:
    engine = _banco_antigo(tmp_path / "antigo.db", dias_desde_o_saldo=0)
    migrar(engine)
    with engine.begin() as c:
        c.execute(text("UPDATE saldo SET saldo_disponivel = 5"))
    migrar(engine)  # não pode recalcular por cima
    assert _ler(engine)[1] == Decimal("5")


def test_migracao_sem_tabela_saldo_nao_faz_nada(tmp_path: Path) -> None:
    migrar(create_engine(f"sqlite:///{(tmp_path / 'vazio.db').as_posix()}"))
