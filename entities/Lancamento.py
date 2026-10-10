# Importamos o BaseModel da biblioteca Pydantic para validar os dados

from pydantic import BaseModel

#Criamos a classe que define a estrutura de um lançamento financeiro

class LancamentoSchema(BaseModel):
    id: int             #Identificador unico do lançament
    descricao: str      #Descrição do gasto ou ganho (ex: "Salário
    valor: float        # Valor monetário (ex: 150.50)
    tipo: str           # Tipo do lançamento: "receita" ou "despesa"
