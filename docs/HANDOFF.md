# 🤜 Handoff Técnico: Squad-AI Remediation

Este documento serve como o ponto de entrada para o **@dev** iniciar a resolução dos débitos técnicos mapeados no projeto **Squad-AI**.

## 1. Contexto do Projeto
O **Squad-AI** é um sistema multi-agente funcional baseado em **CrewAI** e **Streamlit**. Atualmente, opera como um MVP robusto, mas com dívidas técnicas em estabilidade de dados e feedback de interface.

## 2. Estado da Remediação (Sprint 1 & 2 Concluídas)

Atuamos intensamente para estabilizar a base do projeto. Abaixo o status das principais frentes:

### 💾 Banco de Dados
- **[CONCLUÍDO]** Implementação de Alembic. O banco `demandas.db` está versionado (`85a76ae36e62`).
- **[CONCLUÍDO]** Sistema de Backups Automáticos. Snapshots em `backups/` após cada execução.
- **[PENDENTE]** Normalização da tabela `tags` (atualmente JSON string).

### 🎨 UX & Frontend
- **[CONCLUÍDO]** Logs em tempo real usando `st.status`. Transparência total no loop dos agentes.
- **[CONCLUÍDO]** Validação defensiva de formulários (título/descrição obrigatórios).

### 🧪 Qualidade
- **[CONCLUÍDO]** Suíte de testes base com 4 testes de fundação passando.

## 3. Próximos Passos Sugeridos (Roadmap)
1. **Normalização de Dados**: Separar as tags em uma tabela dedicada para facilitar BI e buscas complexas.
2. **CI/CD**: Configurar GitHub Actions para rodar a suíte `pytest` em cada PR.
3. **Refatoração de Crew**: Modularizar a configuração de agents/tasks em arquivos YAML separados por domínio se a equipe crescer.

- **Arquitetura & Sistema**: [system-architecture.md](file:///home/romarck/Documentos/Projetos/Squad-AI/docs/architecture/system-architecture.md)
- **Banco de Dados & Schema**: [SCHEMA.md](file:///home/romarck/Documentos/Projetos/Squad-AI/supabase/docs/SCHEMA.md) | [DB-AUDIT.md](file:///home/romarck/Documentos/Projetos/Squad-AI/supabase/docs/DB-AUDIT.md)
- **Frontend & UX**: [frontend-spec.md](file:///home/romarck/Documentos/Projetos/Squad-AI/docs/frontend/frontend-spec.md)
- **Assessment de Débitos**: [technical-debt-assessment.md](file:///home/romarck/Documentos/Projetos/Squad-AI/docs/prd/technical-debt-assessment.md)

## 3. Guia de Execução (Prioridade Zero)

O planejamento de remediação está organizado no [epic-technical-debt.md](file:///home/romarck/Documentos/Projetos/Squad-AI/docs/stories/epic-technical-debt.md).

### Sprints Recomendadas:
1.  **Fundação (DB)**: Implementar Alembic para gerenciar o esquema atual.
    - 📄 [Story 1.1: Database Migrations](file:///home/romarck/Documentos/Projetos/Squad-AI/docs/stories/story-1.1-db-migrations.md)
2.  **Visibilidade (UX)**: Implementar logs em tempo real na interface Streamlit.
    - 📄 [Story 1.2: Real-time UX Logs](file:///home/romarck/Documentos/Projetos/Squad-AI/docs/stories/story-1.2-ux-logs.md)
3.  **Qualidade (DevOps)**: Estruturar suíte de testes unitários.
    - 📄 [Story 1.3: Unit Testing Foundation](file:///home/romarck/Documentos/Projetos/Squad-AI/docs/stories/story-1.3-unit-tests.md)

## 4. Instruções Específicas para @Dev
Ao iniciar o trabalho, utilize o comando `*implement-story <path-da-story>` para manter o padrão AIOS. Priorize a integridade do banco de dados `demandas.db` existente.

---
— Orion, orquestrando o sistema 🎯
