"""
Modelos Pydantic do recurso "evento".

A separação entre EventoCreate / EventoPublic / EventoInterno existe
justamente para resolver o problema do Exercício 3: o modelo interno
carrega campos operacionais (id do organizador para uso interno e
token de auditoria) que NUNCA devem vazar para o cliente da API.
"""
from datetime import date
from pydantic import BaseModel


class EventoCreate(BaseModel):
    """Payload que o cliente envia para criar um evento."""
    nome: str
    data: date
    organizador: str


class EventoPublic(BaseModel):
    """
    O que a API deve devolver ao cliente.
    Note que NÃO existe aqui nenhum campo de auditoria/id interno.
    Esse é o response_model usado no endpoint de criação (Exercício 3).
    """
    id: int
    nome: str
    data: date
    organizador: str


class EventoInterno(EventoPublic):
    """
    Representação completa, usada apenas internamente (ex: banco de
    dados / times de operação). Contém campos sensíveis que não devem
    ser expostos:
      - organizador_id: identificador interno do organizador (poderia
        ser usado em ataques de enumeração se exposto).
      - audit_token: token interno de auditoria/rastreamento.
    """
    organizador_id: int
    audit_token: str
