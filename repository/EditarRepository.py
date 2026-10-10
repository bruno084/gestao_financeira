from typing import Optional
from sqlalchemy.orm import Session
from entities.ProdutoModel import ProdutoModel
from entities.Schemas import ProdutoUpdate

def atualizar_produto(db: Session, produto_id: int, dados_atualizacao: ProdutoUpdate) -> Optional[ProdutoUpdate]:
    # 1. Busca o produto na base de dados pelo seu ID unico
    produto = db.query(ProdutoModel).filter(ProdutoModel.id == produto_id).first() # type: ignore

    # 2. Se o produto nao existir na base de dados, retorna o None para a camada do controller tratar o erro
    if not produto:
        return None
    # 3. Converte os dados recebidos do Pydantic num dicionario.
    # 'exclude_unset = True' garante que apenas os campos enviados explicitamente pelo utilizador/front-end.
    # sejam atualizados, preservando os valores dos campos nao enviados.
    dados_dict = dados_atualizacao.model_dump(exclude_unset = True)

    # 4. Percorre cada par de campo/valor do dicionario para atualizar o objeto
    for chave, valor in dados_dict.items():
        # Se o campo a atualizar for a 'categoria' (Enum), extraimos a string (.value) para salvar corretamente no banco
        if chave == "categoria" and valor is not None:
            valor = valor.value
        # 'setattr' atualiza dinamicamente o atributo do produto (ex: produto.nome = valor)
        setattr(produto, chave, valor)

    # 5. Efetiva a transacao no ficheiro banco.db
    db.commit()

    # 6. Atualiza o objeto 'produto' com os novos dados gravados na base de dados
    db.refresh(produto)

    # 7. Retorna o produto com os dados atualizados
    return produto