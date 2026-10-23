"""Validação de entrada e formato de saída (camelCase) da API."""
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, PlainSerializer, field_serializer, model_validator
from pydantic.alias_generators import to_camel

from entities.tempo import para_iso_utc

_serializar_float = PlainSerializer(float, return_type=float, when_used="json")

# Dinheiro de entrada/saída: nunca negativo, até 12 dígitos e 2 casas (igual à coluna do banco).
Dinheiro = Annotated[Decimal, Field(ge=0, max_digits=12, decimal_places=2), _serializar_float]
# Valor que pode ser negativo (ex.: saldo restante quando o orçamento estoura).
Valor = Annotated[Decimal, _serializar_float]
Quantidade = Annotated[int, Field(strict=True, ge=0, le=999_999_999)]


class Categoria(str, Enum):
    HIGIENE = "HIGIENE"
    COMIDA = "COMIDA"
    LIMPEZA = "LIMPEZA"
    OUTRO = "OUTRO"


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, str_strip_whitespace=True)


# ---------- Produtos ----------
class ProdutoIn(CamelModel):
    """Corpo do POST e do PUT (substituição completa)."""
    nome: str = Field(min_length=2, max_length=100)
    categoria: Categoria
    quantidade: Quantidade
    preco_unitario: Dinheiro


class ProdutoUpdate(CamelModel):
    """Corpo do PATCH (atualização parcial): só os campos enviados mudam."""
    nome: str | None = Field(None, min_length=2, max_length=100)
    categoria: Categoria | None = None
    quantidade: Quantidade | None = None
    preco_unitario: Dinheiro | None = None

    @model_validator(mode="after")
    def _validar_campos_enviados(self) -> "ProdutoUpdate":
        enviados = self.model_fields_set
        if not enviados:
            raise ValueError("Envie ao menos um campo para atualizar.")
        for campo in enviados:
            if getattr(self, campo) is None:
                raise ValueError(f"O campo {campo} não pode ser nulo.")
        return self


class ProdutoOut(ProdutoIn):
    model_config = ConfigDict(from_attributes=True)

    id: int
    criado_em: datetime

    @field_serializer("criado_em")
    def _serializar_criado_em(self, valor: datetime) -> str:
        return para_iso_utc(valor)


# ---------- Saldo ----------
class SaldoUpdate(CamelModel):
    saldo_mensal: Dinheiro


class SaldoOut(CamelModel):
    model_config = ConfigDict(from_attributes=True)

    saldo_mensal: Dinheiro
    data_saldo: datetime | None = None

    @field_serializer("data_saldo")
    def _serializar_data_saldo(self, valor: datetime | None) -> str | None:
        return para_iso_utc(valor) if valor else None


# ---------- Resumo financeiro ----------
class GastoPorCategoria(CamelModel):
    categoria: Categoria
    total: Dinheiro


class ResumoFinanceiro(CamelModel):
    saldo_mensal: Dinheiro
    total_gasto: Dinheiro
    saldo_restante: Valor
    excedeu_saldo: bool
    por_categoria: list[GastoPorCategoria]
