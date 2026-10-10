from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

# Importamos o motor do banco e a Base do database.py
from database import engine, Base

# IMPORTANTE: Importamos o ProdutoModel para o SQLAlchemy reconhecer a tabela no banco
import entities.ProdutoModel

# Importamos os roteadores (routers) de cada funcionalidade criada nos controllers
from controllers.CriarController import router as criar_router
from controllers.ConsultarController import router as consultar_router  # <--- Adicionado
from controllers.DeletarController import router as deletar_router      # <--- Adicionado
from controllers.EditarController import router as editar_router        # <--- Adicionado

# CRIA AUTOMATICAMENTE A TABELA 'produtos' E O ARQUIVO 'banco.db' AO INICIAR
Base.metadata.create_all(bind=engine)

# Inicializamos a aplicação FastAPI
app = FastAPI(title="API Gestão Financeira")

# Configuração de CORS para liberar conexões do front-end
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Accept"],
)

# Registramos todos os roteadores na aplicação principal
app.include_router(criar_router)      # Rota POST /api/produtos
app.include_router(consultar_router)  # Rota GET /api/produtos
app.include_router(deletar_router)    # Rota DELETE /api/produtos/{id}
app.include_router(editar_router)     # Rota PUT /api/produtos/{id}

# Handler personalizado para formatar erros de validação no padrão com o campo "message" que o front exige
@app.exception_handler(RequestValidationError)
async def erro_validacao(_: Request, exc: RequestValidationError) -> JSONResponse:
    campos = ", ".join(sorted({str(e["loc"][-1]) for e in exc.errors()}))
    return JSONResponse(status_code=422, content={"message": f"Dados inválidos: {campos}."})

# Handler para erros HTTP genéricos
@app.exception_handler(StarletteHTTPException)
async def erro_http(_: Request, exc: StarletteHTTPException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"message": str(exc.detail)})

# Rota de Teste na raiz
@app.get("/")
def home():
    return {"status": "Servidor rodando e tabela 'produtos' criada com sucesso!"}