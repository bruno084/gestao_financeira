from typing import Optional
from sqlalchemy.orm import Session
from entities.ProdutoModel import ProdutoModel


def listar_produtos(db: Session, ordem: Optional[str] = None, limit: Optional[int] = None):
    # 1. Inicia a consulta base na tabela de produtos
    query = db.query(ProdutoModel)

    # 2. Se o front mandar ordem = "recentes", ordena o mais novo para o mais antigo
    if ordem == "recentes":
        query = query.order_by(ProdutoModel.criado_em.desc())

    # 3. Se o front mandar limit, pega apenas os N primeiros
    if limit is not None:
        query = query.limit(limit)

    # 4. Executa a busca e retorna a lista de objetos do banco
    return query.all()


def buscar_produtos_por_nome(db: Session, nome_busca: str):
    # 1. Pega todos os produtos salvos no banco de dados usando o ProdutoModel importado
    todos_produtos = db.query(ProdutoModel).all()

    # 2. Converte o termo que veio do front-end para minúsculo (.lower())
    termo_limpo = nome_busca.lower()

    # 3. LIST COMPREHENSION: Filtra os itens onde o termo está no nome (tudo em minúsculo)
    produtos_filtrados = [
        produto for produto in todos_produtos
        if termo_limpo in produto.nome.lower()
    ]

    return produtos_filtrados