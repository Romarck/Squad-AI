# Story 1.3: Unit Testing Foundation

## Contexto
O projeto não possuía automação de testes. Criamos a base com pytest, mas precisamos de testes reais para a lógica da database e integração dos agentes.

## Descrição
Como Desenvolvedor, quero expandir a suíte de testes unitários para cobrir operações CRUD do banco e mocks de execução da CrewAI.

## Critérios de Aceite
- [x] Diretório `tests/` criado com `conftest.py`.
- [x] Testes para `DemandaDB` (criar, listar, atualizar).
- [x] Mock de `kickoff()` da CrewAI para testes de integração rápidos.

## Estimativa
8 horas.
