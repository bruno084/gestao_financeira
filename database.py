# Importando as funcoes do SQLAlchemy para conectar ao banco SQLite
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Nome do arquivo de banco de dados que será criado automaticamente (3 barras)
SQLALCHEMY_DATABASE_URL = "sqlite:///./banco.db"

# Engine (motor) que conecta ao arquivo SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Fabrica para criar sessoes com o banco de dados
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para mapear as tabelas
Base = declarative_base()

# Funcao para abrir e fechar a conexao do banco a cada requisicao
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()