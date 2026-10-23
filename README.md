# gestao_financeira

API do ControleDeEstoque (FastAPI + SQLAlchemy + SQLite).

## Rodar no localhost
```bash
python -m venv .venv
.venv\Scripts\activate          # Windows  (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
- API: http://localhost:8000 · documentação interativa: http://localhost:8000/docs
- O `banco.db` é criado ao lado do `main.py` na primeira execução (pode iniciar o servidor de qualquer pasta).
- Para manter dados antigos, copie seu `banco.db` para esta pasta antes de iniciar; a tabela `saldo` é criada sozinha.
- Front: sirva a pasta do front (ex.: `npx serve .`) em qualquer porta de `localhost`/`127.0.0.1` e use `API_BASE_URL = 'http://localhost:8000/api'`.

## Testes
```bash
pip install -r requirements-dev.txt
pytest
```
Os testes usam um banco temporário e não tocam no `banco.db`.

## Endpoints (JSON em camelCase)
| Método | Rota | Corpo / resposta |
|---|---|---|
| GET | `/api/produtos?ordem=recentes&limit=4&busca=arroz` | `[{id, nome, categoria, quantidade, precoUnitario, criadoEm}]` |
| POST | `/api/produtos` | `{nome, categoria, quantidade, precoUnitario}` → 201 + produto |
| PUT | `/api/produtos/{id}` | mesmo corpo do POST (todos os campos) → produto |
| PATCH | `/api/produtos/{id}` | só os campos a alterar → produto |
| DELETE | `/api/produtos/{id}` | 200 + produto removido |
| GET | `/api/saldo` | `{saldoMensal, dataSaldo}` |
| PUT | `/api/saldo` | `{saldoMensal}` → `{saldoMensal, dataSaldo}` |
| GET | `/api/financeiro/resumo` | `{saldoMensal, totalGasto, saldoRestante, excedeuSaldo, porCategoria:[{categoria,total}]}` |

- Categorias: `HIGIENE`, `COMIDA`, `LIMPEZA`, `OUTRO`.
- Erros: 4xx/5xx sempre como `{ "message": "texto para o usuário" }`.
- `criadoEm` e `dataSaldo` saem em UTC com `Z` (ex.: `2026-10-23T00:32:30.272Z`).
- Gasto = soma de `quantidade × precoUnitario` de todos os itens; `saldoRestante` fica negativo (e `excedeuSaldo` vira `true`) quando passa do saldo.

## Variáveis de ambiente (opcionais)
- `DATABASE_URL`: outro banco (padrão: `sqlite:///.../banco.db`).
- `CORS_ORIGINS`: origens extras separadas por vírgula, para quando o front for hospedado.
