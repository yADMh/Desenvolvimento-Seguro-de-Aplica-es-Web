"""
Router dedicado ao recurso "eventos".

Exercício 2: todas as rotas específicas do domínio de eventos vivem
aqui, não em main.py. Um novo desenvolvedor que precisar mexer em
"inscrições" ou "usuários" no futuro vai criar routes/inscricoes.py
ou routes/usuarios.py, sem tocar neste arquivo — é exatamente esse
isolamento que evita o problema relatado no contexto do Exercício 2
(uma alteração em rota de pagamentos quebrando rota de notificações
por estarem no mesmo arquivo).
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from database import db
from models.evento import EventoCreate, EventoPublic

router = APIRouter(prefix="/eventos", tags=["eventos"])

templates = Jinja2Templates(directory="templates")


# ---------------------------------------------------------------------
# Rotas JSON (API "de verdade")
# ---------------------------------------------------------------------

@router.get("", response_model=list[EventoPublic])
def listar_eventos():
    """Lista todos os eventos cadastrados (apenas campos públicos)."""
    return db.listar_eventos()


@router.post("", response_model=EventoPublic, status_code=201)
def criar_evento(payload: EventoCreate):
    """
    Cria um evento.

    Exercício 3: o response_model=EventoPublic garante que, mesmo que
    o objeto interno (EventoInterno) tenha organizador_id e
    audit_token, esses campos são filtrados antes de virar JSON de
    resposta. O FastAPI serializa o retorno de acordo com o schema
    do response_model, não com o objeto Python original.
    """
    evento = db.criar_evento(
        nome=payload.nome, data=payload.data, organizador=payload.organizador
    )
    return evento


@router.post("/sem-response-model", status_code=201)
def criar_evento_sem_response_model(payload: EventoCreate):
    """
    Versão ALTERNATIVA (apenas para o exercício comparativo).

    Sem response_model, o FastAPI serializa o objeto Python retornado
    tal como ele é — incluindo organizador_id e audit_token. Isso é
    o cenário de vazamento descrito no Exercício 3.
    """
    evento = db.criar_evento(
        nome=payload.nome, data=payload.data, organizador=payload.organizador
    )
    return evento  # <- devolve o EventoInterno inteiro, sem filtro


@router.get("/{evento_id}", response_model=EventoPublic)
def obter_evento(evento_id: int):
    evento = db.obter_evento(evento_id)
    if evento is None:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    return evento


# ---------------------------------------------------------------------
# Rotas HTML (Exercícios 5 e 6) — reaproveitam a MESMA camada de dados
# ---------------------------------------------------------------------

@router.get("/pagina/lista", response_class=HTMLResponse)
def pagina_lista_eventos(request: Request):
    """
    Renderiza a listagem de eventos em HTML, reaproveitando
    db.listar_eventos() — a mesma função usada pela rota JSON acima.
    Nenhuma lógica de acesso a dados é duplicada.
    """
    eventos = db.listar_eventos()
    return templates.TemplateResponse(
        request=request, name="eventos_list.html", context={"eventos": eventos}
    )


@router.get("/pagina/{evento_id}", response_class=HTMLResponse)
def pagina_detalhe_evento(request: Request, evento_id: int):
    evento = db.obter_evento(evento_id)
    if evento is None:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    return templates.TemplateResponse(
        request=request, name="evento_detail.html", context={"evento": evento}
    )
