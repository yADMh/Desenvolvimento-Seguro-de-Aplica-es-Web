from sqlmodel import SQLModel, Field
from typing import Optional
from pydantic import ConfigDict

class Evento(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    descricao: str

class EventoCreate(SQLModel):
    nome: str
    descricao: str
    # Bloqueia campos extras nao documentados (Mass Assignment)
    model_config = ConfigDict(extra='forbid')
