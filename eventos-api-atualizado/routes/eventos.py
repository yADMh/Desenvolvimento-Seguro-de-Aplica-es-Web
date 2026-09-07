from fastapi import APIRouter, Query, HTTPException, Depends
import re
from sqlmodel import Session, select
from database.db import get_session
from models.evento import Evento

router = APIRouter()

# Ex 1: Validacao por Regex
@router.get("/eventos/busca")
def buscar_eventos(nome: str = Query(..., description="Nome do evento")): 
    if not re.match(r"^[a-zA-Z0-9À-ÿ\s]+$", nome):
        raise HTTPException(status_code=400, detail="Caracteres inválidos na busca")
    return {"message": "Busca segura", "termo": nome}
