from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from service.FinanceiroService import FinanceiroService
from repository.ConsultarRepository import listar_produtos, buscar_produtos_por_nome
from database import get_db

router = APIRouter(prefix = "/financeiro", tags = ["Financeiro"])

class SaldoSchema(BaseModel):
    saldo_mensal: float

@router.put("/saldo")
def atualizar_saldo(dados: SaldoSchema):
    try:
        FinanceiroService.atualizar_saldo(dados.saldo_mensal)
        return {
            "mensagem": "Saldo atualizado com sucesso!",
            "saldo_mensal": dados.saldo_mensal
        }
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))

@router.get("/verificar-orcamento")
def verificar_orcamento(db: Session = Depends(get_db)):
    try:
        produtos = listar_produtos(db)           # Busca os produtos do banco usando a função existente
        resultado = FinanceiroService.verificar_orcamento((produtos))   # Passa para o service calcular a logica de verdade/falso
        return resultado
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))

@router.get("/produtos/buscar")
def buscar_produtos(nome: str, db: Session = Depends(get_db)):
    try:
        produtos_filtrados = buscar_produtos_por_nome(db, nome)
        return {
            "termo_pesquisado": nome,
            "quantidade_encontrada": len(produtos_filtrados),
            "produtos": produtos_filtrados
        }
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))