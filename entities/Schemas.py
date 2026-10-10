# Este arquivo valida os dados que vem do front-end e transforma em camelCase
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field, PlainSerializer
from pydantic.alias_generators import to_camel

# Tipo especial para formatar dinheiro corretamente
Dinheiro = Annotated[
    Decimal,
    Field(ge=0, max_digits=12, decimal_places=2),
    PlainSerializer(float, return_type=float, when_used="json"),
]

# Categorias aceitas pelo front-end
class Categoria(str, Enum):
    HIGIENE = "HIGIENE"
    COMIDA = "COMIDA"
    LIMPEZA = "LIMPEZA"
    OUTRO = "OUTRO"

# Configuração para aceitar/gerar camelCase (ex: precoUnitario)
class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, str_strip_whitespace=True
    )

# Modelo dos dados para Criar/Atualizar um produto
class ProdutoIn(CamelModel):
    nome: str = Field(min_length=2, max_length=100)
    categoria: Categoria
    quantidade: int = Field(ge=0, le=999_999_999)
    preco_unitario: Dinheiro

# Modelo dos dados para Atualizar um produto parcialmente (PATCH/PUT)
class ProdutoUpdate(CamelModel):
    nome: Optional[str] = Field (None, min_length = 2, max_length = 100)
    categoria: Optional[Categoria] = None
    quantidade: Optional[int] = Field(None, ge = 0, le = 999_999_999)
    preco_unitario: Optional[Dinheiro] =  None

# Modelo dos dados que retornam para o front-end
class ProdutoOut(ProdutoIn):
    id: int
    criado_em: datetime
