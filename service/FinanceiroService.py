import json
class FinanceiroService:
    @staticmethod
    def atualizar_saldo(novo_saldo: float):
        # Le o arquivo atual para manter os dois campos se existirem
        try:
            with open("saldo.json", "r") as f:
                dados = json.load(f)
        except Exception:
            dados = {}

        # Atualiza ambos ou o principal
        dados["saldo_mensal"] = novo_saldo
        dados["saldo_disponivel"] = novo_saldo
        with open("saldo.json", "w") as f:
            json.dump(dados, f, ident = 4)
        return novo_saldo

    @staticmethod
    def verificar_orcamento(produtos):
        # Le o saldo mensal do JSON
        with open("saldo.json", "r") as f:
            dados = json.load(f)
        saldo_mensal = dados.get("saldo_mensal", 0.0)

        # Calcula o total do estoque ('preco * quantidade')

        valor_total_estoque = sum(p.preco * p.quantidade for p in produtos)

        # Subtrai do saldo mensal
        saldo_restante = saldo_mensal - valor_total_estoque
        status = saldo_restante <= 0

        return {
            "status": status,       # True se dentro do orcamento, False se estourar
            "saldo_mensal": saldo_mensal,
            "valor_total_estoque":valor_total_estoque,
            "saldo_restante": saldo_restante,
            "mensagem": "Dentro do orçamento!" if status else "Atenção: O estoque ultrapassou o saldo mensal!"
        }