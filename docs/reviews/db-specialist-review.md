# Database Specialist Review - Squad-AI

## Débitos Validados
| ID | Débito | Severidade | Horas | Prioridade | Notas |
|----|--------|------------|-------|------------|-------|
| DB-01 | Falta de Migrations | Med | 4 | Alta | Alembic/Prisma seriam ideais. |
| DB-02 | Tipagem JSON (Tags) | Baixa | 2 | Baixa | SQLite suporta JSON1; usar colunas reais é melhor. |

## Débitos Adicionados
- **Falta de Backup Automático**: Não há rotina de exportação do .db.
- **Conexões não fechadas**: Possível vazamento de conexão no singleton se não tratado no exit do Streamlit.

## Respostas ao Architect
- *Pergunta:* O SQLite é suficiente?
- *Resposta:* Para o MVP sim, mas se escalarmos para 100+ usuários simultâneos, o locking do SQLite será um gargalo. Migrar para PostgreSQL (Supabase/Neon) é recomendado para a próxima fase.

## Recomendações
1. Priorizar Migrations (Alembic).
2. Adicionar script de backup diário do demandas.db.
