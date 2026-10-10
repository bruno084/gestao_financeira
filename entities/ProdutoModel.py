# Este arquivo diz ao SQLite quais colunas e tabela produtos terá

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Numeric, DateTime
from database import Base

# Modelo da tabela no banco de dados SQLite
class ProdutoModel(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    categoria = Column(String(20), nullable=False)
    quantidade = Column(Integer, nullable=False)
    preco_unitario = Column(Numeric(10, 2), nullable=False)
    # Define o campo de data/hora padrão com timezone UTC
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))
