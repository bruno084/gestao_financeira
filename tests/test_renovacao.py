from datetime import date

import pytest

from service.Renovacao import proxima_renovacao, renovacoes_ate


@pytest.mark.parametrize(
    ("inicio", "hoje", "esperado"),
    [
        (date(2026, 7, 9), date(2026, 7, 9), 0),    # no próprio dia
        (date(2026, 7, 9), date(2026, 8, 8), 0),    # falta um dia
        (date(2026, 7, 9), date(2026, 8, 9), 1),    # dia 09 do mês 8: soma de novo
        (date(2026, 7, 9), date(2026, 12, 9), 5),
        (date(2026, 7, 9), date(2027, 7, 8), 11),   # vira o ano
        (date(2026, 7, 9), date(2027, 7, 9), 12),
        (date(2026, 11, 9), date(2027, 1, 9), 2),
        (date(2026, 7, 9), date(2026, 6, 1), 0),    # data anterior ao início: nunca negativo
        (date(2027, 1, 31), date(2027, 2, 27), 0),  # dia 31 em fevereiro
        (date(2027, 1, 31), date(2027, 2, 28), 1),  # renova no último dia do mês curto
        (date(2027, 1, 31), date(2027, 3, 1), 1),
        (date(2027, 1, 31), date(2027, 3, 31), 2),  # e volta ao dia 31
        (date(2028, 1, 31), date(2028, 2, 29), 1),  # ano bissexto
    ],
)
def test_renovacoes_ate(inicio: date, hoje: date, esperado: int) -> None:
    assert renovacoes_ate(inicio, hoje) == esperado


@pytest.mark.parametrize(
    ("inicio", "hoje", "esperado"),
    [
        (date(2026, 7, 9), date(2026, 7, 9), date(2026, 8, 9)),
        (date(2026, 7, 9), date(2026, 8, 9), date(2026, 9, 9)),
        (date(2026, 11, 9), date(2026, 12, 20), date(2027, 1, 9)),  # vira o ano
        (date(2027, 1, 31), date(2027, 1, 31), date(2027, 2, 28)),
        (date(2027, 1, 31), date(2027, 3, 1), date(2027, 3, 31)),
    ],
)
def test_proxima_renovacao(inicio: date, hoje: date, esperado: date) -> None:
    assert proxima_renovacao(inicio, hoje) == esperado
