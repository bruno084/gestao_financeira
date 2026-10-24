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
| GET | `/api/saldo` | `{saldoMensal, saldoDisponivel, dataSaldo}` |
| PUT | `/api/saldo` | `{saldoMensal}` → `{saldoMensal, saldoDisponivel, dataSaldo}` |
| GET | `/api/financeiro/resumo` | `{saldoMensal, totalCreditado, totalGasto, saldoDisponivel, excedeuSaldo, proximaRenovacao, porCategoria:[{categoria,total}]}` |

- Categorias: `HIGIENE`, `COMIDA`, `LIMPEZA`, `OUTRO`.
- Erros: 4xx/5xx sempre como `{ "message": "texto para o usuário" }`.
- `criadoEm` e `dataSaldo` saem em UTC com `Z` (ex.: `2026-10-23T00:32:30.272Z`).
## Como o saldo funciona
Tabela `saldo` (uma linha só): `saldo_mensal`, `data_saldo`, `saldo_disponivel`, `total_creditado`, `renovacoes_aplicadas`.

- **Saldo mensal**: valor fixo que entra todo mês (quanto a pessoa quer gastar por mês com o estoque).
- **Saldo disponível**: o que ainda pode ser usado em itens. Fica **gravado no banco** e não é recalculado a partir do estoque.
- **Primeiro salvamento** (`PUT /api/saldo`): o valor entra no saldo disponível e o dia fica registrado em `data_saldo`.
  Ex.: salvar R$ 200,00 em 09/07 → disponível 200,00; em 09/08 entram mais 200,00; em 09/09, mais 200,00.
- **Renovação**: não há agendador. A cada consulta, o back-end soma os meses que já passaram (`service/Renovacao.py`, dia em Brasília, UTC-3). `renovacoes_aplicadas` impede somar o mesmo mês duas vezes. Em meses curtos, o dia 29/30/31 cai no último dia do mês.
- **Cadastrar item** (`POST`): desconta `quantidade × preço` do saldo disponível, na mesma transação que grava o item.
- **Aumentar** quantidade ou preço (`PUT`/`PATCH`): desconta só a diferença.
- **Diminuir** quantidade ou preço e **excluir** item: **não devolvem** nada ao saldo.
- **Trocar o valor mensal**: o saldo disponível muda pela diferença (200 → 300 soma 100; 300 → 200 tira 100). O dia da renovação continua o do primeiro salvamento. Salvar o mesmo valor não faz nada.
- O saldo disponível pode ficar **negativo** (`excedeuSaldo: true`); o item é cadastrado mesmo assim.
- `totalGasto = totalCreditado − saldoDisponivel`. `porCategoria` mostra o valor dos itens que estão no estoque agora (por isso pode ser menor que o gasto, se houve exclusões).
- Os UPDATEs são atômicos no banco, então duas requisições ao mesmo tempo não se atropelam.

## Bancos antigos
Se o seu `banco.db` veio de uma versão anterior (sem as colunas novas), o servidor as cria sozinho ao iniciar (`migracoes.py`) e preenche com o que a tela mostrava: disponível = creditado − valor atual do estoque.

## Variáveis de ambiente (opcionais)
- `DATABASE_URL`: outro banco (padrão: `sqlite:///.../banco.db`).
- `CORS_ORIGINS`: origens extras separadas por vírgula, para quando o front for hospedado.
