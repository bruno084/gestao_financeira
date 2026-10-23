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
    assert client.get("/api/saldo").json() == {"saldoMensal": 0.0, "dataSaldo": None}


def test_salvar_saldo_persiste_e_registra_data(client: TestClient) -> None:
    r = client.put("/api/saldo", json={"saldoMensal": 1500.5})
    assert r.status_code == 200 and r.json()["saldoMensal"] == 1500.5 and r.json()["dataSaldo"].endswith("Z")
    assert client.get("/api/saldo").json()["saldoMensal"] == 1500.5


@pytest.mark.parametrize("corpo", [{}, {"saldoMensal": -1}, {"saldoMensal": "abc"}, {"saldoMensal": 1.005}])
def test_saldo_invalido(client: TestClient, corpo: dict) -> None:
    assert client.put("/api/saldo", json=corpo).status_code == 422


# ---------- Resumo financeiro ----------
def test_resumo_vazio(client: TestClient) -> None:
    assert client.get("/api/financeiro/resumo").json() == {
        "saldoMensal": 0.0, "totalGasto": 0.0, "saldoRestante": 0.0, "excedeuSaldo": False, "porCategoria": [],
    }


def test_resumo_dentro_do_saldo(client: TestClient) -> None:
    client.put("/api/saldo", json={"saldoMensal": 100})
    criar(client, ARROZ)  # 21,00
    criar(client, SABAO)  # 12,00
    r = client.get("/api/financeiro/resumo").json()
    assert r["totalGasto"] == 33.0 and r["saldoRestante"] == 67.0 and r["excedeuSaldo"] is False
    assert r["porCategoria"] == [{"categoria": "COMIDA", "total": 21.0}, {"categoria": "LIMPEZA", "total": 12.0}]


def test_resumo_estourado_tem_restante_negativo(client: TestClient) -> None:
    client.put("/api/saldo", json={"saldoMensal": 20})
    criar(client, ARROZ)
    r = client.get("/api/financeiro/resumo").json()
    assert r["saldoRestante"] == -1.0 and r["excedeuSaldo"] is True


def test_resumo_acompanha_edicao_e_exclusao(client: TestClient) -> None:
    client.put("/api/saldo", json={"saldoMensal": 50})
    p = criar(client, ARROZ)
    client.patch(f"/api/produtos/{p['id']}", json={"quantidade": 1})
    assert client.get("/api/financeiro/resumo").json()["totalGasto"] == 10.5
    client.delete(f"/api/produtos/{p['id']}")
    assert client.get("/api/financeiro/resumo").json()["totalGasto"] == 0.0


def test_resumo_soma_sem_erro_de_ponto_flutuante(client: TestClient) -> None:
    for _ in range(3):
        criar(client, {**ARROZ, "quantidade": 1, "precoUnitario": 0.1})
    assert client.get("/api/financeiro/resumo").json()["totalGasto"] == 0.3


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
