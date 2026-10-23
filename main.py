"""API Gestão Financeira. Iniciar com: uvicorn main:app --reload --port 8000"""
import logging
import os
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware

import entities.ProdutoModel  # noqa: F401  (registra a tabela 'produtos')
import entities.SaldoModel  # noqa: F401  (registra a tabela 'saldo')
from controllers.ConsultarController import router as consultar_router
from controllers.CriarController import router as criar_router
from controllers.DeletarController import router as deletar_router
from controllers.EditarController import router as editar_router
from controllers.FinanceiroController import router as financeiro_router
from controllers.SaldoController import router as saldo_router
from database import Base, SessionLocal, engine
from repository.SaldoRepository import obter_ou_criar_saldo

logger = logging.getLogger("gestao_financeira")


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        obter_ou_criar_saldo(db)  # garante a linha única do saldo antes de receber requisições
    yield


app = FastAPI(title="API Gestão Financeira", lifespan=lifespan)

_MENSAGENS_PADRAO = {"Not Found": "Recurso não encontrado.", "Method Not Allowed": "Método não permitido."}


async def capturar_erros_inesperados(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    """Transforma qualquer falha inesperada em JSON {"message"}. Fica DENTRO do CORS (é adicionado antes),
    então a resposta de erro 500 também leva os cabeçalhos CORS e o front consegue ler a mensagem."""
    try:
        return await call_next(request)
    except Exception:
        logger.exception("Erro inesperado em %s %s", request.method, request.url.path)
        return JSONResponse(status_code=500, content={"message": "Erro interno do servidor. Tente novamente."})


app.add_middleware(BaseHTTPMiddleware, dispatch=capturar_erros_inesperados)

# Aceita o front em qualquer porta de localhost/127.0.0.1. Ao hospedar, defina CORS_ORIGINS="https://seu-site.com".
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Content-Type", "Accept"],
)

for router in (criar_router, consultar_router, editar_router, deletar_router, saldo_router, financeiro_router):
    app.include_router(router)


@app.exception_handler(RequestValidationError)
async def erro_validacao(_: Request, exc: RequestValidationError) -> JSONResponse:
    nomes: set[str] = set()
    for erro in exc.errors():
        ultimo = erro["loc"][-1] if erro["loc"] else "body"
        nomes.add("corpo da requisição" if ultimo == "body" or isinstance(ultimo, int) else str(ultimo))
    return JSONResponse(status_code=422, content={"message": f"Dados inválidos: {', '.join(sorted(nomes))}."})


@app.exception_handler(StarletteHTTPException)
async def erro_http(_: Request, exc: StarletteHTTPException) -> JSONResponse:
    detalhe = str(exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"message": _MENSAGENS_PADRAO.get(detalhe, detalhe)})


@app.get("/")
def home() -> dict[str, str]:
    return {"status": "Servidor rodando."}
