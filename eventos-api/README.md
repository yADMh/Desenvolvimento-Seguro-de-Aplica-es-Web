# eventos-api

API REST em FastAPI para gestão de eventos (MVP em migração de Java Spring para Python).

## Como rodar

```bash
python3 -m virtualenv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/uvicorn main:app --reload
```

Acesse:
- `GET /` — status do serviço
- `GET /eventos` e `POST /eventos` — API JSON
- `GET /eventos/pagina/lista` — listagem em HTML
- `GET /eventos/pagina/{id}` — detalhe em HTML

## Estrutura de módulos

```
eventos-api/
├── main.py          # cria o FastAPI app e registra routers (sem rotas de domínio)
├── routes/          # um arquivo por recurso (ex: eventos.py) com o APIRouter e os endpoints
├── models/          # schemas Pydantic (request/response) de cada recurso
├── database/         # acesso a dados (hoje simulado em memória; troque por um ORM aqui)
└── templates/        # templates Jinja2 (base.html + páginas que o estendem)
```

**routes/** — é aqui que um novo desenvolvedor procura ou adiciona endpoints HTTP.
Cada recurso (eventos, futuramente inscrições, usuários) ganha seu próprio arquivo
e seu próprio `APIRouter`, registrado em `main.py` via `include_router`.

**models/** — define os formatos de entrada (`EventoCreate`) e saída (`EventoPublic`)
de cada recurso. É aqui que se decide explicitamente o que a API expõe ao cliente,
separado do modelo interno (`EventoInterno`) usado só internamente.

**database/** — concentra toda lógica de leitura/escrita de dados. Rotas JSON e rotas
HTML chamam as mesmas funções daqui, então não há duplicação de lógica de acesso a
dados entre elas.

**templates/** — HTML renderizado pelo Jinja2. `base.html` contém cabeçalho/rodapé
compartilhados; as demais páginas usam `{% extends "base.html" %}`.

## Por que separar routers por recurso (Exercício 2)

Manter cada recurso em seu próprio `APIRouter` isola o raio de impacto de qualquer
mudança: uma alteração nas rotas de eventos não pode quebrar silenciosamente rotas de
outro domínio, porque elas vivem em arquivos e objetos `APIRouter` diferentes. Isso
também torna o onboarding mais previsível — um novo desenvolvedor sabe que "rotas de X"
estão em `routes/x.py`, sem precisar perguntar a quem escreveu o código original — e
permite que times diferentes evoluam recursos diferentes em paralelo com baixo risco de
conflito, já que `main.py` nunca precisa ser editado além de um `include_router` novo.
