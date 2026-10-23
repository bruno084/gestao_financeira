import os
import tempfile
from collections.abc import Iterator
from pathlib import Path

# Banco temporário: definido ANTES de importar a aplicação, para os testes nunca tocarem no banco.db real.
os.environ["DATABASE_URL"] = f"sqlite:///{Path(tempfile.mkdtemp(), 'teste.db').as_posix()}"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402


@pytest.fixture()
def client() -> Iterator[TestClient]:
    from database import Base, engine
    from main import app

    Base.metadata.drop_all(engine)
    with TestClient(app) as c:  # o 'with' dispara o lifespan (cria tabelas e a linha do saldo)
        yield c
