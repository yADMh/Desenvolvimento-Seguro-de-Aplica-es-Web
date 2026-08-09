"""
Camada de acesso a dados (simulada em memória).

Isolar isso em seu próprio módulo é o que permite, no Exercício 5,
reaproveitar a MESMA fonte de dados tanto na rota JSON (GET /eventos)
quanto na rota HTML (GET /eventos/pagina), sem duplicar lógica de
acesso a dados entre as duas.
"""
import itertools
import secrets

from models.evento import EventoInterno

_id_counter = itertools.count(start=1)

# "Banco de dados" em memória: id -> EventoInterno
_eventos_db: dict[int, EventoInterno] = {}


def criar_evento(nome: str, data, organizador: str) -> EventoInterno:
    novo_id = next(_id_counter)
    evento = EventoInterno(
        id=novo_id,
        nome=nome,
        data=data,
        organizador=organizador,
        organizador_id=1000 + novo_id,          # campo interno
        audit_token=secrets.token_hex(8),        # campo interno
    )
    _eventos_db[novo_id] = evento
    return evento


def listar_eventos() -> list[EventoInterno]:
    return list(_eventos_db.values())


def obter_evento(evento_id: int) -> EventoInterno | None:
    return _eventos_db.get(evento_id)
