"""
Ponto de entrada da aplicação.

Exercício 2: este arquivo NÃO contém nenhuma rota específica do
domínio de eventos — apenas cria a aplicação e registra os routers
de cada recurso via include_router. Quando o serviço crescer para
incluir inscrições e usuários, basta importar e incluir novos
routers aqui, sem alterar routes/eventos.py.
"""
from fastapi import FastAPI

from routes import eventos

app = FastAPI(title="eventos-api")

app.include_router(eventos.router)


@app.get("/")
def status():
    """Rota de status usada para validar que o ambiente está no ar (Exercício 1)."""
    return {"status": "ok", "service": "eventos-api"}
