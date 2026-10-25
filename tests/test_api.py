import pytest
from fastapi.testclient import TestClient

ARROZ = {"nome": "Arroz", "categoria": "COMIDA", "quantidade": 2, "precoUnitario": 10.5}
SABAO = {"nome": "Sabão", "categoria": "LIMPEZA", "quantidade": 3, "precoUnitario": 4}


def criar(client: TestClient, corpo: dict) -> dict:
    r = client.post("/api/produtos", json=corpo)
    assert r.status_code == 201, r.text
    return r.json()


# ---------- Produtos ----------
def test_criar_e_listar(client: TestClient) -> None:
    p = criar(client, ARROZ)
    assert p["id"] == 1 and p["precoUnitario"] == 10.5 and p["categoria"] == "COMIDA"
    assert client.get("/api/produtos").json() == [p]


def test_data_sai_em_utc_com_z(client: TestClient) -> None:
    assert criar(client, ARROZ)["criadoEm"].endswith("Z")


def test_listar_recentes_com_limite(client: TestClient) -> None:
    for i in range(5):
        criar(client, {**ARROZ, "nome": f"Item {i}"})
    r = client.get("/api/produtos", params={"ordem": "recentes", "limit": 4}).json()
    assert [p["nome"] for p in r] == ["Item 4", "Item 3", "Item 2", "Item 1"]


def test_parametros_invalidos_na_listagem(client: TestClient) -> None:
    assert client.get("/api/produtos", params={"ordem": "x"}).status_code == 422
    assert client.get("/api/produtos", params={"limit": 0}).status_code == 422


def test_busca_ignora_curingas_do_like(client: TestClient) -> None:
    criar(client, ARROZ)
    criar(client, {**ARROZ, "nome": "100% Suco"})
    assert [p["nome"] for p in client.get("/api/produtos", params={"busca": "arr"}).json()] == ["Arroz"]
    assert [p["nome"] for p in client.get("/api/produtos", params={"busca": "%"}).json()] == ["100% Suco"]


@pytest.mark.parametrize(
    "mudanca",
    [
        {"nome": "A"},
        {"categoria": "BEBIDA"},
        {"quantidade": -1},
        {"quantidade": 1.5},
        {"quantidade": "2"},
        {"precoUnitario": -0.01},
        {"precoUnitario": 1.234},
    ],
)
def test_criar_rejeita_dados_invalidos(client: TestClient, mudanca: dict) -> None:
    r = client.post("/api/produtos", json={**ARROZ, **mudanca})
    assert r.status_code == 422 and r.json()["message"].startswith("Dados inválidos: ")


def test_criar_rejeita_corpo_vazio_e_json_quebrado(client: TestClient) -> None:
    assert client.post("/api/produtos", json={}).status_code == 422
    r = client.post("/api/produtos", content="{quebrado", headers={"Content-Type": "application/json"})
    assert r.status_code == 422 and "message" in r.json()


def test_put_substitui_tudo(client: TestClient) -> None:
    p = criar(client, ARROZ)
    r = client.put(f"/api/produtos/{p['id']}", json={**ARROZ, "quantidade": 5, "precoUnitario": 11})
    assert r.status_code == 200 and r.json()["quantidade"] == 5 and r.json()["criadoEm"] == p["criadoEm"]
    assert client.put(f"/api/produtos/{p['id']}", json={"quantidade": 5}).status_code == 422


def test_patch_altera_so_o_enviado(client: TestClient) -> None:
    p = criar(client, ARROZ)
    r = client.patch(f"/api/produtos/{p['id']}", json={"quantidade": 9})
    assert r.status_code == 200
    assert r.json()["quantidade"] == 9 and r.json()["nome"] == "Arroz" and r.json()["precoUnitario"] == 10.5


@pytest.mark.parametrize("corpo", [{}, {"nome": None}, {"quantidade": None}])
def test_patch_rejeita_vazio_e_nulo(client: TestClient, corpo: dict) -> None:
    p = criar(client, ARROZ)
    assert client.patch(f"/api/produtos/{p['id']}", json=corpo).status_code == 422


def test_editar_e_excluir_inexistente_dao_404(client: TestClient) -> None:
    assert client.put("/api/produtos/99", json=ARROZ).status_code == 404
    assert client.patch("/api/produtos/99", json={"quantidade": 1}).status_code == 404
    r = client.delete("/api/produtos/99")
    assert r.status_code == 404 and r.json() == {"message": "Produto não encontrado."}


def test_id_invalido_na_url(client: TestClient) -> None:
    assert client.delete("/api/produtos/abc").status_code == 422


def test_excluir(client: TestClient) -> None:
    p = criar(client, ARROZ)
    assert client.delete(f"/api/produtos/{p['id']}").json()["id"] == p["id"]
    assert client.get("/api/produtos").json() == []


# ---------- Saldo ----------
def test_saldo_comeca_zerado(client: TestClient) -> None:
    assert client.get("/api/saldo").json() == {"saldoMensal": 0.0, "saldoDisponivel": 0.0, "dataSaldo": None}


def test_primeiro_salvamento_credita_o_valor_e_registra_o_dia(client: TestClient) -> None:
    r = client.put("/api/saldo", json={"saldoMensal": 1500.5})
    assert r.status_code == 200
    assert r.json()["saldoMensal"] == 1500.5 and r.json()["saldoDisponivel"] == 1500.5
    assert r.json()["dataSaldo"].endswith("Z")
    assert client.get("/api/saldo").json()["saldoDisponivel"] == 1500.5


@pytest.mark.parametrize("corpo", [{}, {"saldoMensal": -1}, {"saldoMensal": "abc"}, {"saldoMensal": 1.005}])
def test_saldo_invalido(client: TestClient, corpo: dict) -> None:
    assert client.put("/api/saldo", json=corpo).status_code == 422


def test_salvar_o_mesmo_valor_nao_muda_nada(client: TestClient) -> None:
    primeira = client.put("/api/saldo", json={"saldoMensal": 200}).json()
    criar(client, ARROZ)
    segunda = client.put("/api/saldo", json={"saldoMensal": 200}).json()
    assert segunda["dataSaldo"] == primeira["dataSaldo"] and segunda["saldoDisponivel"] == 179.0


def test_mudar_o_valor_ajusta_o_disponivel_pela_diferenca(client: TestClient) -> None:
    primeira = client.put("/api/saldo", json={"saldoMensal": 200}).json()["dataSaldo"]
    criar(client, ARROZ)  # 21,00 -> disponível 179,00
    r = client.put("/api/saldo", json={"saldoMensal": 300}).json()
    assert r["saldoDisponivel"] == 279.0 and r["dataSaldo"] == primeira  # o dia da renovação não muda
    assert client.put("/api/saldo", json={"saldoMensal": 100}).json()["saldoDisponivel"] == 79.0
    assert client.get("/api/financeiro/resumo").json()["totalCreditado"] == 100.0


# ---------- Saldo disponível x itens ----------
def test_cadastrar_item_desconta_do_saldo(client: TestClient) -> None:
    client.put("/api/saldo", json={"saldoMensal": 100})
    criar(client, ARROZ)  # 21,00
    criar(client, SABAO)  # 12,00
    r = client.get("/api/financeiro/resumo").json()
    assert r["saldoDisponivel"] == 67.0 and r["totalGasto"] == 33.0 and r["totalCreditado"] == 100.0
    assert r["excedeuSaldo"] is False
    assert r["porCategoria"] == [{"categoria": "COMIDA", "total": 21.0}, {"categoria": "LIMPEZA", "total": 12.0}]


def test_excluir_item_nao_devolve_saldo(client: TestClient) -> None:
    client.put("/api/saldo", json={"saldoMensal": 100})
    p = criar(client, ARROZ)  # disponível 79,00
    client.delete(f"/api/produtos/{p['id']}")
    r = client.get("/api/financeiro/resumo").json()
    assert r["saldoDisponivel"] == 79.0 and r["totalGasto"] == 21.0
    assert r["porCategoria"] == []  # o estoque ficou vazio, mas o gasto continua contado


def test_diminuir_quantidade_ou_preco_nao_devolve_saldo(client: TestClient) -> None:
    client.put("/api/saldo", json={"saldoMensal": 100})
    p = criar(client, ARROZ)  # disponível 79,00
    client.patch(f"/api/produtos/{p['id']}", json={"quantidade": 1})
    client.patch(f"/api/produtos/{p['id']}", json={"precoUnitario": 1})
    assert client.get("/api/saldo").json()["saldoDisponivel"] == 79.0


def test_aumentar_quantidade_ou_preco_desconta_so_a_diferenca(client: TestClient) -> None:
    client.put("/api/saldo", json={"saldoMensal": 100})
    p = criar(client, ARROZ)  # 2 x 10,50 = 21,00 -> disponível 79,00
    client.patch(f"/api/produtos/{p['id']}", json={"quantidade": 4})  # 42,00: mais 21,00
    assert client.get("/api/saldo").json()["saldoDisponivel"] == 58.0
    client.put(f"/api/produtos/{p['id']}", json={**ARROZ, "quantidade": 4, "precoUnitario": 20})  # 80,00: mais 38,00
    assert client.get("/api/saldo").json()["saldoDisponivel"] == 20.0
    client.put(f"/api/produtos/{p['id']}", json={**ARROZ, "quantidade": 4, "precoUnitario": 20})  # igual: nada muda
    assert client.get("/api/saldo").json()["saldoDisponivel"] == 20.0


def test_saldo_fica_negativo_quando_passa_do_disponivel(client: TestClient) -> None:
    client.put("/api/saldo", json={"saldoMensal": 20})
    criar(client, ARROZ)  # 21,00
    r = client.get("/api/financeiro/resumo").json()
    assert r["saldoDisponivel"] == -1.0 and r["excedeuSaldo"] is True and r["totalGasto"] == 21.0


def test_item_cadastrado_antes_do_saldo_e_descontado(client: TestClient) -> None:
    criar(client, ARROZ)  # sem saldo definido: disponível -21,00
    assert client.get("/api/saldo").json()["saldoDisponivel"] == -21.0
    assert client.put("/api/saldo", json={"saldoMensal": 200}).json()["saldoDisponivel"] == 179.0


def test_item_recusado_nao_desconta_saldo(client: TestClient) -> None:
    client.put("/api/saldo", json={"saldoMensal": 100})
    assert client.post("/api/produtos", json={**ARROZ, "quantidade": -1}).status_code == 422
    assert client.put("/api/produtos/99", json=ARROZ).status_code == 404
    assert client.get("/api/saldo").json()["saldoDisponivel"] == 100.0


def test_resumo_vazio(client: TestClient) -> None:
    assert client.get("/api/financeiro/resumo").json() == {
        "saldoMensal": 0.0, "totalCreditado": 0.0, "totalGasto": 0.0, "saldoDisponivel": 0.0,
        "excedeuSaldo": False, "proximaRenovacao": None, "porCategoria": [],
    }


def test_soma_sem_erro_de_ponto_flutuante(client: TestClient) -> None:
    client.put("/api/saldo", json={"saldoMensal": 1})
    for _ in range(3):
        criar(client, {**ARROZ, "quantidade": 1, "precoUnitario": 0.1})
    r = client.get("/api/financeiro/resumo").json()
    assert r["totalGasto"] == 0.3 and r["saldoDisponivel"] == 0.7 and r["porCategoria"][0]["total"] == 0.3


def test_valores_enormes_nao_quebram(client: TestClient) -> None:
    # 999.999.999 x 9.999.999.999,99 passa de 12 dígitos: a soma não pode ser barrada como se fosse um preço.
    criar(client, {**ARROZ, "quantidade": 999_999_999, "precoUnitario": 9_999_999_999.99})
    r = client.get("/api/financeiro/resumo")
    assert r.status_code == 200 and r.json()["excedeuSaldo"] is True


# ---------- Renovação mensal ----------
def test_saldo_mensal_e_somado_de_novo_a_cada_mes(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    from datetime import timedelta

    from service import Renovacao

    client.put("/api/saldo", json={"saldoMensal": 200})
    criar(client, ARROZ)  # gasto de 21,00
    hoje = Renovacao.hoje_em_brasilia()

    r = client.get("/api/financeiro/resumo").json()
    assert r["totalCreditado"] == 200.0 and r["saldoDisponivel"] == 179.0 and r["proximaRenovacao"] is not None

    monkeypatch.setattr(Renovacao, "hoje_em_brasilia", lambda: hoje + timedelta(days=40))  # 1 renovação
    for _ in range(2):  # consultar de novo não pode somar o mesmo mês outra vez
        r = client.get("/api/financeiro/resumo").json()
        assert r["totalCreditado"] == 400.0 and r["saldoDisponivel"] == 379.0

    monkeypatch.setattr(Renovacao, "hoje_em_brasilia", lambda: hoje + timedelta(days=70))  # 2 renovações
    r = client.get("/api/saldo").json()
    assert r["saldoDisponivel"] == 579.0


def test_meses_sem_acesso_sao_somados_de_uma_vez_e_cadastro_usa_o_saldo_atualizado(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    from datetime import timedelta

    from service import Renovacao

    client.put("/api/saldo", json={"saldoMensal": 200})
    hoje = Renovacao.hoje_em_brasilia()
    monkeypatch.setattr(Renovacao, "hoje_em_brasilia", lambda: hoje + timedelta(days=70))  # 2 meses sem abrir
    criar(client, ARROZ)  # o cadastro soma os 2 meses antes de descontar 21,00
    assert client.get("/api/saldo").json()["saldoDisponivel"] == 579.0


def test_mudar_o_valor_depois_de_meses_fecha_os_meses_com_o_valor_antigo(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    from datetime import timedelta

    from service import Renovacao

    client.put("/api/saldo", json={"saldoMensal": 200})
    hoje = Renovacao.hoje_em_brasilia()
    monkeypatch.setattr(Renovacao, "hoje_em_brasilia", lambda: hoje + timedelta(days=40))  # 1 mês passou
    r = client.put("/api/saldo", json={"saldoMensal": 300}).json()
    assert r["saldoDisponivel"] == 200 + 200 + 100  # inicial + mês fechado com 200 + ajuste da mudança


# ---------- CORS e erros ----------
def test_cors_aceita_localhost_em_qualquer_porta(client: TestClient) -> None:
    for origem in ("http://localhost:3000", "http://127.0.0.1:5500"):
        r = client.options("/api/produtos/1", headers={"Origin": origem, "Access-Control-Request-Method": "PATCH"})
        assert r.status_code == 200 and r.headers["access-control-allow-origin"] == origem


def test_cors_recusa_origem_desconhecida(client: TestClient) -> None:
    r = client.options("/api/produtos", headers={"Origin": "https://malicioso.example", "Access-Control-Request-Method": "POST"})
    assert r.status_code == 400 and "access-control-allow-origin" not in r.headers


def test_erro_inesperado_vira_json_com_cors(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    import controllers.ConsultarController as ctrl

    def falhar(**_: object) -> None:
        raise RuntimeError("segredo interno")

    monkeypatch.setattr(ctrl, "listar_produtos", falhar)
    r = client.get("/api/produtos", headers={"Origin": "http://localhost:3000"})
    assert r.status_code == 500
    assert r.json() == {"message": "Erro interno do servidor. Tente novamente."}
    assert "segredo" not in r.text
    assert r.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_rota_inexistente_em_portugues(client: TestClient) -> None:
    r = client.get("/api/nada")
    assert r.status_code == 404 and r.json() == {"message": "Recurso não encontrado."}
