from fastapi import APIRouter, Depends
#from html5lib.constants import prefixes
from sqlalchemy.orm import Session

# Funcao de conexao com o banco de dados
from database import get_db

# Importamos o Schemas de entrada/saida e a funcao saida do repositorio
from entities.Schemas import ProdutoIn, ProdutoOut
from repository.CriarRepository import salvar_no_banco

# Criamos o router com o prefixo /api exigido pelo front-end
router = APIRouter(prefix = "/api", tags=["Produtos"])

# Rota POST /api/produtos que retorna o ProdutoOut com o codigo HTTP 201 (Criado)
@router.post("/produtos", response_model = ProdutoOut, status_code = 201)
def criar_produto(item: ProdutoIn, db: Session = Depends(get_db)):
    # Chama o repositorio enviando a sessao do banco (db) e os dados do formulario (item)
    return salvar_no_banco(db = db, item = item)