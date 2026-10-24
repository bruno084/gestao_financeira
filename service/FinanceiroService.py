from decimal import Decimal

from sqlalchemy.orm import Session

from entities.Schemas import Categoria, GastoPorCategoria, ResumoFinanceiro
from repository.FinanceiroRepository import somar_gastos_por_categoria
from repository.SaldoRepository import aplicar_renovacoes
from service import Renovacao

_CATEGORIAS_VALIDAS = {c.value for c in Categoria}


class FinanceiroService:
    @staticmethod
    def montar_resumo(db: Session) -> ResumoFinanceiro:
        """Os valores do saldo vêm prontos do banco; aqui só se calcula o gasto e a próxima renovação."""
        saldo = aplicar_renovacoes(db)

        proxima = None
        if saldo.data_saldo is not None:
            proxima = Renovacao.proxima_renovacao(
                Renovacao.data_em_brasilia(saldo.data_saldo), Renovacao.hoje_em_brasilia()
            )

        # Valor dos itens que estão no estoque agora (por categoria). É informativo: o gasto do saldo
        # não diminui quando um item é excluído.
        por_categoria: dict[Categoria, Decimal] = {}
        for categoria, total in somar_gastos_por_categoria(db):
            # Categoria desconhecida (dado antigo no banco) entra em OUTRO em vez de derrubar o resumo.
            chave = Categoria(categoria if categoria in _CATEGORIAS_VALIDAS else Categoria.OUTRO.value)
            por_categoria[chave] = por_categoria.get(chave, Decimal("0")) + total

        return ResumoFinanceiro(
            saldo_mensal=saldo.saldo_mensal,
            total_creditado=saldo.total_creditado,
            total_gasto=saldo.total_creditado - saldo.saldo_disponivel,
            saldo_disponivel=saldo.saldo_disponivel,
            excedeu_saldo=saldo.saldo_disponivel < 0,
            proxima_renovacao=proxima,
            por_categoria=[
                GastoPorCategoria(categoria=c, total=t)
                for c, t in sorted(por_categoria.items(), key=lambda item: item[1], reverse=True)
            ],
        )
