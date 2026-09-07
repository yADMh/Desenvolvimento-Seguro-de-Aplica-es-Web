# Relatório Técnico - TP2 (Correções de Segurança)

Este pacote contém as correções aplicadas nos exercícios 1 a 8, organizadas em módulos conforme solicitado:
1. **Exercício 1**: Validação de regex implementada na rota de busca (routes/eventos.py) para evitar SQL Injection.
2. **Exercício 2**: Relatório sobre as vulnerabilidades OWASP no arquivo principal.
3. **Exercício 3 e 4**: Prevenção de BOLA com middleware de dependência de JWT e modelo com `extra='forbid'` (models/evento.py).
4. **Exercício 5**: Auto-escape e output encoding no Jinja2 ativados ao remover a flag `| safe` (templates/evento_detail.html).
5. **Exercício 6**: CORS configurado estritamente e SecurityHeadersMiddleware no main.py.
6. **Exercício 7**: Implementado `slowapi` limitando especificamente as rotas sensíveis como `/login` a 5 por minuto.
7. **Exercício 8**: Implementação do `SQLModel` e `BaseSettings` lendo .env via `pydantic-settings` (config.py e database/db.py).
