from datetime import datetime, timezone
from sqlalchemy.orm import Session

# Importamos o modelo da tabela no SQLite
from entities.ProdutoModel import ProdutoModel

# Importamos o Schema com a validacao Pydantic
from entities.Schemas import ProdutoIn

# Funcao responsavel por inserir o produto no banco de dados SQLite
def salvar_no_banco(db: Session, item: ProdutoIn):
    # Criamos a instância do produto passando valores recebidos e o datetime explicito
    novo_produto = ProdutoModel(
        nome = item.nome,
        categoria = item.categoria.value,   # Converte o Enum em texto ("HIGIENE", "COMIDA", etc.)
        quantidade = item.quantidade,
        preco_unitario = item.preco_unitario,
        criado_em = datetime.now(timezone.utc) # Adciona a data/hora atual UTC no objeto
    )

    # Prepara o INSERT no banco
    db.add(novo_produto)

    # Salva permanentemente no arquivo banco.db
    db.commit()

    # Atualiza o objeto local para carregar o ID gerado automaticamente pelo banco
    db.refresh(novo_produto)

    # Retorna o produto cadastrado
    return novo_produto
