# Relatório — eventos-api

## Exercício 1 — Ambiente validado

```
$ ./venv/bin/uvicorn main:app --reload --port 8000
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.

$ curl http://127.0.0.1:8000/
{"status":"ok","service":"eventos-api"}
```

`requirements.txt` gerado via `pip freeze` após instalar fastapi e uvicorn no venv:

```
fastapi==0.141.1
Jinja2==3.1.6
pydantic==2.13.4
pydantic_core==2.46.4
starlette==1.6.0
uvicorn==0.52.1
```

## Exercício 3 — response_model: comparação e risco

**Com `response_model=EventoPublic`:**
```json
{"id": 1, "nome": "Meetup Python", "data": "2026-09-15", "organizador": "Ana Souza"}
```

**Sem `response_model` (endpoint `/eventos/sem-response-model`):**
```json
{
  "id": 2, "nome": "Workshop FastAPI", "data": "2026-09-20", "organizador": "Bruno Lima",
  "organizador_id": 1002,
  "audit_token": "62083f40ca1127ce"
}
```

**Explicação (o que vaza e o impacto):** sem `response_model`, o FastAPI serializa o
objeto Python retornado exatamente como ele é, então `organizador_id` (identificador
interno) e `audit_token` (usado internamente para auditoria) aparecem na resposta
pública. Na prática, isso permite que qualquer cliente da API colete IDs internos
sequenciais de organizadores — a mesma classe de falha que, segundo o relato do colega,
já facilitou um ataque de enumeração em outro serviço da empresa, permitindo mapear ou
adivinhar organizadores válidos para tentativas de acesso indevido. O `audit_token`
exposto também deixa de servir como controle interno confiável, já que passa a ser
visível a terceiros.

## Exercício 6 — XSS e auto-escape do Jinja2

**Reprodução:** payload `{"nome": "<script>alert(1)</script>", ...}` enviado via
`POST /eventos`. O HTML gerado por `GET /eventos/pagina/lista` contém:

```html
<td><a href="/eventos/pagina/1">&lt;script&gt;alert(1)&lt;/script&gt;</a></td>
```

**Explicação (até 6 linhas):** é um risco real, não apenas teórico — nomes de eventos
não são digitados só por usuários "bem-comportados"; qualquer campo de texto livre pode
receber HTML/JS malicioso, seja por engano, teste ou ataque deliberado. Se esse
conteúdo fosse inserido na página sem tratamento, o navegador executaria o script no
contexto da sessão de quem visualiza a página (roubo de cookies, ações em nome do
usuário, etc. — um XSS refletido/armazenado clássico). O Jinja2, por padrão, faz
auto-escape de variáveis inseridas com `{{ }}` em templates `.html`: caracteres como
`<`, `>` e `&` são convertidos em entidades HTML (`&lt;`, `&gt;`) antes de renderizar,
então o navegador exibe o texto literal em vez de interpretá-lo como marcação/script.

## Exercício 7 — Análise CIA

| Pilar | Situação atual | Lacuna |
|---|---|---|
| **Confidencialidade** | `response_model=EventoPublic` filtra `organizador_id` e `audit_token` nas rotas oficiais de eventos. | O endpoint de demonstração `/eventos/sem-response-model` (e qualquer novo endpoint criado sem response_model) continua expondo dados internos — não há teste ou lint automatizado que impeça isso. Também não há autenticação: qualquer um pode ler `/eventos`. |
| **Integridade** | Os modelos Pydantic (`EventoCreate`) validam tipo e formato dos campos enviados (ex: `data` precisa ser uma data válida), rejeitando payloads malformados com erro 422. | Não há verificação de quem está criando o evento (sem autenticação/autorização), então qualquer cliente pode criar ou, no futuro, alterar eventos em nome de outro organizador. Não há trilha de auditoria persistida (o `audit_token` é gerado mas não é gravado em log/BD real). |
| **Disponibilidade** | O serviço roda em processo único do uvicorn com reload, adequado para desenvolvimento. | Não há rate limiting, timeout configurado nem múltiplos workers/health checks — uma rota lenta ou um cliente malicioso enviando muitas requisições pode indisponibilizar o serviço inteiro para todos os usuários. Esse tipo de lacuna tende a ser subestimado quando a revisão foca só em confidencialidade, como já observado em outros times. |

## Exercício 8 — DFD e mapeamento de frameworks

**Fluxo de dados sensível e trust boundary:** o nome/dados do organizador entram pelo
navegador do usuário (zona não confiável) → cruzam a trust boundary na borda da API
FastAPI, onde passam por validação Pydantic (`EventoCreate`) → são processados e
persistidos na camada `database/` (zona confiável, hoje simulada em memória) → ao
sair novamente em direção ao cliente, cruzam a trust boundary de volta e passam pelo
filtro do `response_model` (JSON) ou pelo auto-escape do Jinja2 (HTML) antes de deixar
a zona confiável.

| Framework | Área de aplicação | Controle concreto já discutido |
|---|---|---|
| **OWASP** (Top 10 / ASVS) | Prevenção de vulnerabilidades na camada de aplicação web | Auto-escape do Jinja2 mitigando XSS (Exercício 6); `response_model` mitigando exposição excessiva de dados / "Broken Object Property Level Authorization" (Exercício 3) |
| **NIST SSDF** (Secure Software Development Framework) | Práticas de ciclo de vida seguro de desenvolvimento | Isolamento de dependências via virtualenv + `requirements.txt` versionado (Exercício 1); separação em módulos `routes/models/database` reduzindo superfície de erro e facilitando revisão de código (Exercício 4) |
| **MITRE** (ATT&CK / CWE) | Catalogação de técnicas de ataque e fraquezas de código | CWE-79 (XSS) relacionado ao Exercício 6; CWE-213/CWE-200 (exposição de informação sensível) relacionado ao endpoint sem `response_model` do Exercício 3 |

O diagrama de fluxo de dados abaixo ilustra essas fronteiras.
