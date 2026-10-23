"""Conexão com o SQLite e utilitários de sessão."""
import os
import warnings
from collections.abc import Iterator
from pathlib import Path
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.exc import SAWarning
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# O SQLite guarda NUMERIC como número de ponto flutuante; os valores são sempre
# arredondados para 2 casas na leitura e na soma, então o aviso é ruído.
warnings.filterwarnings("ignore", message=r".*does \*not\* support Decimal.*", category=SAWarning)

BASE_DIR = Path(__file__).resolve().parent

# Caminho absoluto: o banco é sempre o mesmo, não importa de qual pasta o servidor foi iniciado.
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{(BASE_DIR / 'banco.db').as_posix()}")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    """Base de todos os modelos ORM."""


def get_db() -> Iterator[Session]:
    """Abre uma sessão por requisição; desfaz a transação se algo falhar."""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


DbSession = Annotated[Session, Depends(get_db)]
