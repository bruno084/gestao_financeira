from typing import Optional
from sqlalchemy.orm import Session
from entities.ProdutoModel import ProdutoModel

def listar_produtos(db: Session, ordem: Optional[str] = None, limit: Optional[int] = None):
    # 1. Inicia a consulta base na tabela de produtos
    query = db.query(ProdutoModel)

    # 2. Se o front mandar ordem = "recentes", ordena o mais novo para o mais antigo
    if ordem == "recentes":
        query = query.order_by(ProdutoModel.criado_em.desc())

    # 3. Se o front mandar limit = 4, pega apenas os N primeiros
    if limit is not None:
        query = query.limit(limit)

    # 4. Executa a busca e retorna a lista de objetos do banco
    return query.all()
