import json
from datetime import datetime

class FinanceiroService:
    @staticmethod
    def atualizar_saldo(novo_saldo: float):
        # Tenta ler o arquivo saldo.json existente
        try:
            with open("saldo.json", "r") as f:
                dados = json.load(f)
        except Exception:
            dados = {}

        # Atualiza os valores do saldo e adiciona a data atual em formato ISO
        dados["saldo_mensal"] = novo_saldo
        dados["saldo_disponivel"] = novo_saldo
        dados["data_saldo"] = datetime.now().isoformat()

        # Salva tudo de volta no arquivo saldo.json com indentação bonita
        with open("saldo.json", "w") as f:
            json.dump(dados, f, indent=4)

        return dados

    @staticmethod
    def verificar_orcamento(produtos):
        # Lê o saldo atual do arquivo JSON
        with open("saldo.json", "r") as f:
            dados = json.load(f)

        saldo_mensal = dados.get("saldo_mensal", 0.0)

        # Calcula o total do estoque multiplicando preco por quantidade de cada produto
        valor_total_estoque = sum(p.preco * p.quantidade for p in produtos)

        # Subtrai o valor do estoque do saldo mensal
        saldo_restante = saldo_mensal - valor_total_estoque
        status = saldo_restante >= 0  # True se o saldo cobre o estoque, False se estourou

        return {
            "status": status,
            "saldo_mensal": saldo_mensal,
            "valor_total_estoque": valor_total_estoque,
            "saldo_restante": saldo_restante,
            "mensagem": "Dentro do orçamento!" if status else "Atenção: O estoque ultrapassou o saldo mensal!"
        }