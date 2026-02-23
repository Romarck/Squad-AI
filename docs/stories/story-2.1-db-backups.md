# Story 2.1: Automated DB Backups

## Contexto
O banco de dados SQLite é um arquivo local sem redundância. Uma falha de disco ou erro acidental pode causar perda de dados históricos.

## Descrição
Como SysAdmin/Dev, quero um mecanismo automatizado para fazer backup do `demandas.db` após cada execução bem-sucedida ou diariamente.

## Critérios de Aceite
- [ ] Script Python para exportar dump do SQL ou cópia do .db para pasta `backups/`.
- [ ] Integração no fluxo do Streamlit para disparar backup pós-execução.

## Estimativa
2 horas.
