# Technical Debt Assessment - DRAFT

## Para Revisão dos Especialistas

### 1. Débitos de Sistema
- **Manifesto Incompleto**: Dependências como Streamlit e SQLAlchemy não estão no `pyproject.toml`.
- **Ausência de Testes**: 0% de cobertura de testes automatizados.
- **Acoplamento UI-Logic**: Lógica de execução da Crew diretamente vinculada a componentes Streamlit.

### 2. Débitos de Database
- **Falta de Migrations**: Esquema gerenciado por strings manuais.
- **Tipagem Fraca**: Tags armazenadas como strings JSON.

### 3. Débitos de Frontend/UX
- **Feedback de Longa Duração**: Experiência de espera pode ser melhorada (ex: logs em tempo real).
- **Consistência de Estado**: Risco de perda de estado do Streamlit em recarregamentos acidentais.

## Matriz Preliminar
| ID | Débito | Área | Impacto | Esforço | Prioridade |
|----|--------|------|---------|---------|------------|
| SY-01 | Testes Unitários | Sistema | Alto | Médio | Alta |
| DB-01 | Migrations (Alembic) | Data | Médio | Baixo | Alta |
| UX-01 | Melhora Logs em Tempo Real| UX | Médio | Médio | Média |
| SY-02 | Refatoração Dependências | Sistema | Baixo | Baixo | Média |

## Perguntas para Especialistas
- **@data-engineer**: O SQLite atual é o suficiente para o volume de dados esperado ou devemos considerar PostgreSQL para facilitar migrations no futuro?
- **@ux-design-expert**: Como podemos tornar a espera de 5 minutos do processo mais interativa no Streamlit?

⚠️ PENDENTE: Revisão dos Especialistas.
