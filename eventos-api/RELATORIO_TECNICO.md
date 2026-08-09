# Relatório técnico — decisões de projeto (eventos-api)

Este relatório explica o **porquê** de cada decisão tomada na construção do
`eventos-api`, exercício a exercício. Para os resultados/testes/comparações
em si, ver `REPORT.md`; para a estrutura final do código, ver `README.md`.

## Exercício 1 — Ambiente e bootstrap

Optei por `virtualenv` (em vez de instalar globalmente) porque o requisito
explícito era isolamento de dependências entre projetos na mesma máquina —
um `pip install` global teria resolvido o problema imediato, mas quebraria
a exigência do time de plataforma na primeira vez que outro serviço Python
precisasse de uma versão diferente de alguma lib. O `requirements.txt` foi
gerado via `pip freeze` (em vez de escrito à mão) para capturar exatamente
as versões instaladas e testadas, evitando o clássico "funciona na minha
máquina". Rodei o servidor sem `--reload` só para os testes automatizados
via curl (evita ruído de duplo processo do reloader nos logs), mas o
`--reload` é o modo recomendado para o dia a dia de desenvolvimento, como
pedido na tarefa.

## Exercício 2 — Router por recurso

A decisão central foi criar `routes/eventos.py` com seu próprio
`APIRouter(prefix="/eventos")` em vez de declarar as rotas direto em
`main.py`. Isso não é só estética: com routers separados, o "raio de
explosão" de qualquer mudança fica contido no arquivo do recurso. É a
mesma causa raiz do incidente relatado no contexto (rota de pagamentos
quebrando rota de notificações) — quando tudo mora no mesmo arquivo,
qualquer erro de sintaxe ou import quebrado derruba o módulo inteiro,
inclusive rotas não relacionadas. `main.py` ficou reduzido a
`app.include_router(...)`, então adicionar `routes/inscricoes.py` no
futuro é uma linha nova ali, não uma edição de arquivo existente.

## Exercício 3 — Filtragem explícita de resposta

Decidi modelar três classes Pydantic em vez de uma só:
`EventoCreate` (entrada), `EventoPublic` (o que o cliente pode ver) e
`EventoInterno` (o que existe de fato no "banco", com `organizador_id` e
`audit_token`). A camada de dados sempre trabalha com `EventoInterno` —
é o objeto real do domínio — e é o `response_model=EventoPublic` na rota
que decide o que sai. Essa separação foi proposital: se eu tivesse usado
um único modelo "flexível" com campos opcionais, seria fácil esquecer de
marcar um campo novo como interno no futuro. Com três classes distintas,
adicionar um campo sensível significa adicionar em `EventoInterno` e
**não** em `EventoPublic` — a omissão vira a proteção, em vez de exigir
que alguém lembre de mascarar manualmente cada resposta. Mantive também um
endpoint espelho sem `response_model` (`/sem-response-model`) só para
efeito de comparação pedida no exercício; ele não deveria existir em um
serviço real.

## Exercício 4 — Reorganização em módulos

A divisão escolhida foi `routes/` (HTTP), `models/` (schemas) e
`database/` (acesso a dados), o padrão mais comum em projetos FastAPI de
médio porte. Cada módulo tem uma responsabilidade única e previsível:
um desenvolvedor procurando "onde mexer no schema de evento" vai direto a
`models/evento.py`, sem precisar ler `routes/eventos.py` inteiro. Isolar
`database/db.py` também foi o que permitiu, no Exercício 5, reaproveitar a
mesma função `listar_eventos()` na rota JSON e na rota HTML sem duplicar
lógica — se o acesso a dados estivesse espalhado dentro das próprias
funções de rota, essa reutilização exigiria copiar código.

## Exercício 5 — Jinja2 sem duplicar lógica

A rota HTML (`/eventos/pagina/lista`) chama exatamente a mesma função de
banco (`db.listar_eventos()`) usada pela rota JSON (`/eventos`). A
alternativa seria a rota HTML montar sua própria query/filtro — decidi
não fazer isso porque criaria duas fontes de verdade para "quais eventos
existem", que poderiam divergir com o tempo (por exemplo, se alguém
adicionar um filtro de eventos cancelados só em um dos dois lugares).
`Jinja2Templates(directory="templates")` foi instanciado dentro do
próprio módulo de rotas de eventos por simplicidade neste projeto pequeno;
em um serviço com mais recursos HTML eu extrairia isso para um módulo
compartilhado (`templates.py`) para não reinstanciar por router.

## Exercício 6 — Escape por padrão + herança de templates

Não escrevi nenhum código de sanitização manual — decisão deliberada. O
Jinja2 já faz auto-escape por padrão para arquivos com extensão `.html`
carregados via `Jinja2Templates`, então a defesa contra XSS refletido
veio "de graça" simplesmente por usar a ferramenta corretamente, sem
gambiarra. Testei isso na prática enviando o payload `<script>` real, em
vez de apenas assumir que o auto-escape funcionaria. Para o cabeçalho e
rodapé compartilhados, usei herança de templates (`base.html` com
`{% block content %}`) em vez de `{% include %}` de fragmentos, porque
herança deixa explícito, em cada página filha, exatamente qual parte do
layout ela está customizando — reduz o risco do tipo de inconsistência
visual mencionado no contexto do exercício.

## Exercício 7 — Tríade CIA aplicada ao código real

Optei por apontar lacunas **observáveis no código atual**, não riscos
genéricos de FastAPI, porque o pedido era uma análise objetiva para
priorização, não um checklist teórico de segurança. Por isso o exemplo de
confidencialidade cita especificamente o endpoint
`/eventos/sem-response-model` (que existe no próprio repositório) como
lacuna, em vez de um risco hipotético. O ponto de disponibilidade
(ausência de rate limiting/timeouts) foi incluído mesmo sem estar ligado a
nenhum exercício anterior, exatamente porque o contexto avisou que esse
pilar costuma ser subestimado quando a revisão foca só em
confidencialidade.

## Exercício 8 — DFD com fronteiras de confiança

Modelei o DFD com apenas duas zonas (não confiável / confiável) e três
nós dentro da zona confiável (API, armazenamento, resposta filtrada) em
vez de detalhar cada função interna — a meta era deixar visível a
trust boundary e o ponto exato onde a validação/filtragem acontece, não
documentar exaustivamente a arquitetura. Cada controle da tabela
OWASP/NIST SSDF/MITRE foi amarrado a algo que já existe no repositório
(auto-escape, `response_model`, `requirements.txt`, separação de módulos),
para que o diagrama sirva de ponto de partida real para a modelagem de
ameaças formal, e não uma lista de boas práticas desconectada do código.
