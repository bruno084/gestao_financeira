from decimal import Decimal

from sqlalchemy.orm import Session

from entities.Schemas import Categoria, GastoPorCategoria, ResumoFinanceiro
from repository.FinanceiroRepository import somar_gastos_por_categoria
from repository.SaldoRepository import obter_ou_criar_saldo

_CATEGORIAS_VALIDAS = {c.value for c in Categoria}


class FinanceiroService:
    @staticmethod
    def montar_resumo(db: Session) -> ResumoFinanceiro:
        """Gasto = soma de (quantidade x preço) de todo o estoque; compara com o saldo mensal."""
        saldo_mensal = obter_ou_criar_saldo(db).saldo_mensal

        por_categoria: dict[Categoria, Decimal] = {}
        for categoria, total in somar_gastos_por_categoria(db):
            # Categoria desconhecida (dado antigo no banco) entra em OUTRO em vez de derrubar o resumo.
            chave = Categoria(categoria if categoria in _CATEGORIAS_VALIDAS else Categoria.OUTRO.value)
            por_categoria[chave] = por_categoria.get(chave, Decimal("0")) + total

        total_gasto = sum(por_categoria.values(), Decimal("0"))
        saldo_restante = saldo_mensal - total_gasto

        return ResumoFinanceiro(
            saldo_mensal=saldo_mensal,
            total_gasto=total_gasto,
            saldo_restante=saldo_restante,
            excedeu_saldo=saldo_restante < 0,
            por_categoria=[
                GastoPorCategoria(categoria=c, total=t)
                for c, t in sorted(por_categoria.items(), key=lambda item: item[1], reverse=True)
            ],
        )
