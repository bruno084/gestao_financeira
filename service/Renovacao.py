"""Renovação mensal do saldo: todo mês, no mesmo dia em que o saldo foi salvo, o valor é somado de novo."""
import calendar
from datetime import date, datetime, timedelta, timezone

# Horário de Brasília (UTC-3, o Brasil não usa mais horário de verão).
BRASILIA = timezone(timedelta(hours=-3))


def hoje_em_brasilia() -> date:
    return datetime.now(BRASILIA).date()


def data_em_brasilia(momento_utc: datetime) -> date:
    """Converte a data guardada no banco (UTC, sem fuso) para o dia em Brasília."""
    return momento_utc.replace(tzinfo=timezone.utc).astimezone(BRASILIA).date()


def _dia_no_mes(ano: int, mes: int, dia: int) -> date:
    """O dia 31 vira 30, 29 ou 28 em meses mais curtos."""
    return date(ano, mes, min(dia, calendar.monthrange(ano, mes)[1]))


def renovacoes_ate(inicio: date, hoje: date) -> int:
    """Quantas vezes o saldo já foi renovado desde o dia em que foi salvo (0 no próprio dia)."""
    meses = (hoje.year - inicio.year) * 12 + (hoje.month - inicio.month)
    if meses <= 0:
        return 0
    # Neste mês a renovação só acontece a partir do dia combinado.
    if hoje < _dia_no_mes(hoje.year, hoje.month, inicio.day):
        meses -= 1
    return meses


def proxima_renovacao(inicio: date, hoje: date) -> date:
    """Data da próxima vez em que o valor será somado."""
    total_meses = inicio.year * 12 + (inicio.month - 1) + renovacoes_ate(inicio, hoje) + 1
    ano, mes = divmod(total_meses, 12)
    return _dia_no_mes(ano, mes + 1, inicio.day)
