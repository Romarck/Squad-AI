# Squad de Agentes Inteligentes - MVP Desenvolvimento Ágil

Sistema multi-agente baseado em **CrewAI** que automatiza todo o ciclo de desenvolvimento ágil usando IA generativa. Todos os relatórios, documentação e código são gerados **em português brasileiro (pt-BR)**.

## 📑 Índice

- [O que faz este projeto?](#-o-que-faz-este-projeto)
- [Arquitetura](#️-arquitetura)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação](#-instalação)
- [Configuração](#-configuração)
- [Como Usar](#-como-usar)
  - [Interface Web (Recomendado)](#interface-web-recomendado)
  - [Linha de Comando](#linha-de-comando)
- [CRUD de Demandas](#-crud-de-demandas)
- [Troubleshooting](#-troubleshooting)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Ferramentas Customizadas](#️-ferramentas-customizadas)

---

## 🎯 O que faz este projeto?

Este sistema automatiza todo o ciclo de desenvolvimento ágil com 4 agentes especializados:

1. **Product Owner** - Cria user stories estruturadas no Jira (em português)
2. **Analista de Sistemas** - Gera especificações técnicas detalhadas (em português)
3. **Desenvolvedor Python** - Implementa código com comentários e testes (em português)
4. **Quality Assurance** - Valida qualidade e gera relatórios (em português)

**Diferencial**: Todo o conteúdo gerado (user stories, especificações, comentários de código, relatórios) está **inteiramente em português brasileiro (pt-BR)**.

---

## 🏗️ Arquitetura

### Agentes

| Agente | Responsabilidades | Ferramentas | Idioma |
|--------|-------------------|-------------|--------|
| **Product Owner** | Criar user stories no Jira | JiraIntegrationTool, JiraConnectivityTester | pt-BR |
| **Analista de Sistemas** | Gerar especificações técnicas | FileReadTool | pt-BR |
| **Desenvolvedor Python** | Desenvolver código + testes | PytestExecutionSimulator, FileReadTool | pt-BR |
| **Quality Assurance** | Validar qualidade e atualizar Jira | PytestExecutionSimulator, JiraIntegrationTool | pt-BR |

### Workflow

```
Demanda → User Story (Jira) → Especificação Técnica → Código Python → Testes → Validação → Relatório
```

Todos configurados com:
- `language="pt-BR"` no CrewAI
- Instruções explícitas para gerar conteúdo em português
- Gemini 2.0 Flash Lite como modelo de IA

---

## 📋 Pré-requisitos

- **Python** >= 3.10, < 3.14
- **Conta Google Cloud** (para Gemini API) - [Criar chave aqui](https://aistudio.google.com/app/apikey)
- **Conta Jira** (Atlassian) - Opcional para testes locais
- **UV ou pip** para gerenciamento de dependências

---

## 🚀 Instalação

### 1. Navegue até o diretório do projeto

```bash
cd /home/romarck/Documentos/Projetos/Squad-AI
```

### 2. Crie um ambiente virtual

```bash
# Usando UV (recomendado)
uv venv

# OU usando Python padrão
python -m venv .venv
```

### 3. Ative o ambiente virtual

```bash
source .venv/bin/activate
```

### 4. Instale as dependências

**Opção A: Usando UV (mais rápido)**
```bash
uv pip install crewai crewai-tools streamlit
```

**Opção B: Usando pip tradicional**
```bash
pip install crewai[tools] streamlit
```

### 5. Configure o arquivo .env

```bash
# Crie o arquivo .env com as credenciais
nano .env  # ou use seu editor preferido
```

**Conteúdo mínimo do .env:**
```bash
# Google Gemini API (OBRIGATÓRIO)
GEMINI_API_KEY=sua_chave_gemini_aqui

# Jira (OPCIONAL - apenas se quiser integração real com Jira)
JIRA_URL=https://sua-empresa.atlassian.net
JIRA_EMAIL=seu-email@exemplo.com
JIRA_API_KEY=seu_token_jira_aqui
```

#### Como obter as credenciais:

**Gemini API Key** (OBRIGATÓRIO):
1. Acesse: https://aistudio.google.com/app/apikey
2. Faça login com sua conta Google
3. Clique em "Create API Key"
4. Copie a chave gerada

**Jira API Token** (OPCIONAL):
1. Acesse: https://id.atlassian.com/manage-profile/security/api-tokens
2. Clique em "Create API token"
3. Dê um nome (ex: "CrewAI Squad")
4. Copie o token gerado

---

## ⚙️ Configuração

### Validar Instalação

Antes de usar, valide se tudo está configurado corretamente:

```bash
python validate_config.py
```

Você verá:
- ✅ **Versão do Python**: Verificação de compatibilidade
- ✅ **Arquivo .env**: Se existe e está acessível
- ✅ **Variáveis de ambiente**: Se estão definidas
- ✅ **Gemini API**: Teste de conectividade
- ✅ **Jira API**: Teste de conectividade (se configurado)
- ✅ **Dependências**: Se pacotes necessários estão instalados

---

## 🎮 Como Usar

Existem **duas formas** de usar o sistema:

### Interface Web (Recomendado)

A interface web oferece CRUD completo, visualização em tempo real e histórico de demandas.

#### Iniciar a Interface Web

```bash
# Certifique-se de estar no ambiente virtual
source .venv/bin/activate

# Inicie o Streamlit
streamlit run app_completo.py
```

A interface será aberta automaticamente em: **http://localhost:8501**

#### Funcionalidades da Interface Web

**Aba 1: Nova Demanda**
- ✅ Formulário para criar nova demanda
- ✅ Opção de integração com Jira (ON/OFF)
- ✅ Campo para project key do Jira
- ✅ Sistema de tags para organização
- ✅ Execução da Squad com visualização em tempo real

**Aba 2: Histórico**
- ✅ Lista de todas as demandas criadas
- ✅ Pesquisa por título ou descrição
- ✅ Filtro por status (pendente, em andamento, concluída, erro)
- ✅ Ações: Visualizar, Editar, Deletar, Executar
- ✅ Estatísticas de demandas na sidebar

**Aba 3: Execução**
- ✅ Acompanhamento em tempo real da execução
- ✅ Progresso de cada agente
- ✅ Visualização de erros

**Aba 4: Resultados**
- ✅ Visualização detalhada dos resultados
- ✅ Saída de cada agente:
  - Product Owner: User Story criada
  - Analista: Especificação Técnica
  - Desenvolvedor: Código e Testes
  - QA: Relatório de Qualidade

#### Fluxo de Uso da Interface Web

1. **Criar Demanda**: Vá para "Nova Demanda" e preencha os campos
2. **Executar**: Clique em "🚀 Executar Squad"
3. **Acompanhar**: Veja o progresso em tempo real
4. **Ver Resultados**: Acesse a aba "Resultados" para ver o código gerado
5. **Histórico**: Consulte todas as demandas na aba "Histórico"

### Linha de Comando

Para usuários avançados ou automação.

#### Execução Básica

```bash
python main.py run
```

#### Teste Sem Jira

Se você não configurou o Jira, use o teste local:

```bash
python test_local.py
```

Este script executa a Squad **sem** integração com Jira, gerando todo o conteúdo localmente.

#### Execução com Entrada Customizada

Edite `src/squad_de_agentes_inteligentes___mvp_desenvolvimento_agil/main.py`:

```python
def run():
    inputs = {
        'demanda_titulo': 'Validação de CPF',
        'demanda_descricao': 'Criar função para validar CPF brasileiro',
        'project_key': 'DEV',  # ou 'LOCAL' para teste sem Jira
        'spec_file': 'specs/validacao_cpf.md',
        'issue_key': 'DEV-123'  # Opcional
    }
    SquadDeAgentesInteligentesMvpDesenvolvimentoAgilCrew().crew().kickoff(inputs=inputs)
```

Depois execute:
```bash
python main.py run
```

---

## 💾 CRUD de Demandas

O sistema inclui um banco de dados SQLite (`demandas.db`) que armazena:

### Tabela: demandas
- **id**: ID único
- **titulo**: Título da demanda
- **descricao**: Descrição completa
- **usar_jira**: Flag de integração Jira (true/false)
- **project_key**: Chave do projeto Jira ou "LOCAL"
- **status**: pendente | em_andamento | concluida | erro
- **tags**: Tags separadas por vírgula
- **created_at**: Data de criação
- **updated_at**: Última atualização
- **executed_at**: Última execução

### Tabela: resultados
- **id**: ID único
- **demanda_id**: Referência para demanda
- **agente**: Nome do agente (Product Owner, Analista, Desenvolvedor, QA)
- **resultado**: Texto completo do resultado
- **created_at**: Data de criação

### Operações CRUD via Interface Web

- **Create**: Aba "Nova Demanda" → Preencher → Salvar
- **Read**: Aba "Histórico" → Visualizar lista
- **Update**: Aba "Histórico" → Botão "✏️ Editar"
- **Delete**: Aba "Histórico" → Botão "🗑️ Deletar"

### Pesquisa e Filtros

- **Pesquisa por texto**: Busca em título e descrição
- **Filtro por status**: Mostra apenas demandas com status específico
- **Filtro por tags**: Filtra demandas com tags específicas

---

## 🛠️ Troubleshooting

### Erro: "GEMINI_API_KEY not found"

```bash
# Verifique se o .env existe
ls -la .env

# Verifique o conteúdo
cat .env | grep GEMINI_API_KEY

# Se não existir, crie manualmente
echo "GEMINI_API_KEY=sua_chave_aqui" > .env
```

### Erro: "Jira authentication failed" (401 Unauthorized)

**Soluções:**

1. **Teste manual da API Jira**:
```bash
curl -u "seu-email@exemplo.com:SEU_TOKEN" \
  -X GET \
  "https://sua-empresa.atlassian.net/rest/api/3/myself"
```

2. **Gere um novo token** em: https://id.atlassian.com/manage-profile/security/api-tokens

3. **Use modo LOCAL** (sem Jira):
   - Na interface web, desmarque "Usar integração com Jira"
   - No código, use `project_key='LOCAL'`

### Erro: "ModuleNotFoundError: No module named 'crewai'"

```bash
# Ative o ambiente virtual
source .venv/bin/activate

# Reinstale as dependências
uv pip install crewai crewai-tools streamlit
```

### Erro: "Address already in use" (Streamlit)

```bash
# Mate o processo na porta 8501
lsof -ti:8501 | xargs kill -9

# Reinicie o Streamlit
streamlit run app_completo.py
```

### Erro de proxy corporativo

Se você está em ambiente corporativo com proxy:

```bash
# Adicione no .env
HTTP_PROXY=http://proxy.empresa.com:8080
HTTPS_PROXY=https://proxy.empresa.com:8080
```

### Interface Web não está abrindo

```bash
# Execute com modo verbose
streamlit run app_completo.py --server.headless true --server.port 8501 --logger.level=debug
```

---

## 📁 Estrutura do Projeto

```
Squad-AI/
├── README.md                            # Esta documentação
├── .env                                 # Credenciais (não commitar!)
├── .gitignore                          # Arquivos ignorados pelo Git
│
├── app_completo.py                     # 🌟 Interface Web Streamlit (PRINCIPAL)
├── database.py                         # Gerenciamento SQLite
├── demandas.db                        # Banco de dados local
│
├── main.py                             # Entry point CLI
├── validate_config.py                  # Script de validação
├── test_local.py                       # Teste sem Jira
│
├── pyproject.toml                      # Configuração do projeto
├── requirements.txt                    # Dependências (se usar pip)
│
├── src/
│   └── squad_de_agentes_inteligentes___mvp_desenvolvimento_agil/
│       ├── crew.py                     # 🤖 Definição dos 4 agentes
│       ├── crew_runner.py              # Execução com tracking
│       ├── main.py                     # Entry point do crew
│       │
│       ├── config/
│       │   ├── agents.yaml             # ⚙️ Configuração dos agentes (pt-BR)
│       │   └── tasks.yaml              # ⚙️ Configuração das tarefas (pt-BR)
│       │
│       └── tools/
│           ├── jira_integration_tool.py           # Integração Jira
│           ├── jira_connectivity_tester.py        # Teste Jira
│           └── pytest_execution_simulator.py      # Validação Python
│
├── knowledge/                          # Base de conhecimento (opcional)
├── tests/                             # Testes unitários (a implementar)
└── .venv/                             # Ambiente virtual Python
```

### Arquivos Principais

| Arquivo | Descrição | Quando Usar |
|---------|-----------|-------------|
| `app_completo.py` | Interface web completa com CRUD | **Uso diário recomendado** |
| `database.py` | Gerenciamento do banco de dados | Usado automaticamente pela interface |
| `main.py` | Entry point para linha de comando | Automação, scripts, CI/CD |
| `validate_config.py` | Validação de configuração | Antes da primeira execução |
| `test_local.py` | Teste sem integração Jira | Desenvolvimento, demos |
| `src/*/crew.py` | Definição dos agentes | Customização de agentes |
| `src/*/config/agents.yaml` | Configuração de agentes | Ajustar prompts, goals |
| `src/*/config/tasks.yaml` | Configuração de tarefas | Ajustar workflow |

---

## 🛠️ Ferramentas Customizadas

### 1. JiraIntegrationTool

**Funcionalidades:**
- ✅ Criar issues (Task, Story, Bug)
- ✅ Ler issues existentes
- ✅ Adicionar comentários
- ✅ Atualizar status
- ✅ Suporte a proxy corporativo

**Uso:**
```python
from tools.jira_integration_tool import JiraIntegrationTool

tool = JiraIntegrationTool()
result = tool.run(
    action="create_issue",
    project_key="DEV",
    summary="Validação de CPF",
    description="Implementar validação de CPF brasileiro"
)
```

### 2. PytestExecutionSimulator

**Funcionalidades:**
- ✅ Validação de sintaxe Python via AST
- ✅ Simulação de pytest
- ✅ Análise de qualidade de código
- ✅ Métricas de documentação
- ✅ Detecção de erros de sintaxe

**Uso:**
```python
from tools.pytest_execution_simulator import PytestExecutionSimulator

tool = PytestExecutionSimulator()
result = tool.run(
    code_content="def validar_cpf(cpf): ...",
    test_content="def test_validar_cpf(): ..."
)
```

### 3. JiraConnectivityTesterTool

**Funcionalidades:**
- ✅ Teste de autenticação
- ✅ Listagem de projetos acessíveis
- ✅ Validação de permissões
- ✅ Diagnóstico de problemas

**Uso:**
```python
from tools.jira_connectivity_tester import JiraConnectivityTesterTool

tool = JiraConnectivityTesterTool()
result = tool.run(project_key="DEV")
```

---

## 📊 Exemplo de Saída

### Execução Completa (Interface Web)

```
🔄 Product Owner: Testando conectividade com Jira...
✅ Autenticação bem-sucedida! Conectado como: João Silva
✅ Encontrados 3 projetos acessíveis: DEV, PROD, TEST

🔄 Product Owner: Criando user story no Jira...
✅ Issue criada com sucesso: DEV-456

📝 User Story (em português):
Título: Implementar Validação de CPF
Como: desenvolvedor
Quero: uma função de validação de CPF
Para: garantir dados válidos no sistema

Critérios de Aceitação:
1. Validar formato XXX.XXX.XXX-XX
2. Verificar dígitos verificadores
3. Retornar True/False

---

🔄 Analista de Sistemas: Gerando especificação técnica...
✅ Especificação criada (em português)

## Especificação Técnica: Validação de CPF

### Objetivo
Criar função Python para validar CPF brasileiro com verificação de dígitos.

### Implementação
- Arquivo: src/validacao_cpf.py
- Função principal: validar_cpf(cpf: str) -> bool
- Tratamento de erros: ValueError para entradas inválidas

### Casos de Teste
1. CPF válido: "123.456.789-09"
2. CPF inválido: "111.111.111-11"
3. Formato incorreto: "12345678909"

---

🔄 Desenvolvedor Python: Desenvolvendo código...
✅ Sintaxe validada com sucesso!

```python
def validar_cpf(cpf: str) -> bool:
    """
    Valida um número de CPF brasileiro.

    Args:
        cpf: String contendo o CPF no formato XXX.XXX.XXX-XX

    Returns:
        True se o CPF é válido, False caso contrário
    """
    # Remove caracteres não numéricos
    cpf_numeros = ''.join(filter(str.isdigit, cpf))

    # Verifica se tem 11 dígitos
    if len(cpf_numeros) != 11:
        return False

    # Calcula primeiro dígito verificador
    soma = sum(int(cpf_numeros[i]) * (10 - i) for i in range(9))
    digito1 = 11 - (soma % 11)
    if digito1 >= 10:
        digito1 = 0

    # ... resto da implementação
    return True
```

---

🔄 QA: Executando testes...
✅ Validação concluída

## Relatório de Testes (em português)

### Resumo
- ✅ Total de testes: 5
- ✅ Aprovados: 5
- ❌ Reprovados: 0
- 📊 Taxa de sucesso: 100%

### Detalhes
1. ✅ test_cpf_valido :: APROVADO
2. ✅ test_cpf_invalido :: APROVADO
3. ✅ test_formato_incorreto :: APROVADO
4. ✅ test_cpf_nulo :: APROVADO
5. ✅ test_cpf_repetido :: APROVADO

### Checklist de Qualidade
- ✅ Código sintaticamente correto
- ✅ Tratamento de exceções adequado
- ✅ Documentação completa em português
- ✅ Type hints presentes
- ✅ Testes cobrem casos normais e excepcionais

🎉 Execução concluída com sucesso!
```

---

## 🌐 Idioma Português (pt-BR)

### Configuração Aplicada

Todo o sistema está configurado para gerar conteúdo em **português brasileiro**:

**1. Agentes (agents.yaml)**
- Cada agente tem instrução explícita: "SEMPRE em português brasileiro"
- Backstories enfatizam comunicação em pt-BR

**2. Tarefas (tasks.yaml)**
- Todas as tarefas especificam: "INTEIRAMENTE em português brasileiro (pt-BR)"
- Expected outputs incluem: "TUDO em português brasileiro"

**3. Código (crew.py)**
- Todos os 4 agentes têm: `language="pt-BR"`
- Modelo: Gemini 2.0 Flash Lite

### O que é gerado em português:

✅ **Product Owner**
- Título da user story
- Descrição completa
- Critérios de aceitação
- Comentários no Jira

✅ **Analista de Sistemas**
- Especificação técnica completa
- Descrição do objetivo
- Detalhes de implementação
- Cenários de teste

✅ **Desenvolvedor Python**
- Comentários no código
- Docstrings de funções
- Mensagens de erro
- Comentários em testes

✅ **Quality Assurance**
- Relatório de testes
- Checklist de qualidade
- Métricas e estatísticas
- Comentários no Jira

---

## 🔐 Segurança

- **Nunca** commite o arquivo `.env`
- Use tokens de API, não senhas
- Revogue tokens não utilizados regularmente
- Em ambientes corporativos, siga as políticas de proxy
- Não compartilhe seu `demandas.db` publicamente (pode conter informações sensíveis)

---

## 📝 Roadmap e Melhorias Futuras

### Em Planejamento
- [ ] Execução real de pytest (não simulada)
- [ ] Dashboard de métricas e analytics
- [ ] Suporte a múltiplos idiomas
- [ ] Integração com GitHub
- [ ] Webhooks do Jira para automação completa
- [ ] Export de relatórios em PDF
- [ ] Testes unitários completos em `tests/`

### Contribuições

Sugestões são bem-vindas! Áreas prioritárias:
1. Testes unitários
2. Integração com outros issue trackers (GitHub Issues, GitLab)
3. Suporte a outros modelos de IA (GPT-4, Claude)
4. Templates de código customizáveis

---

## 📚 Recursos e Referências

- [Documentação CrewAI](https://docs.crewai.com)
- [Jira REST API v3](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [Google Gemini API](https://ai.google.dev/docs)
- [Streamlit Documentation](https://docs.streamlit.io/)

---

## ⚠️ Limitações Conhecidas

1. **PytestExecutionSimulator**: Simula testes via AST, **não executa código real**
2. **Issue Types Jira**: Atualmente fixado em "Task" (configurável em `tools/jira_integration_tool.py`)
3. **Memória**: Sem contexto persistente entre execuções diferentes
4. **Rate Limits**: Sem controle automático de rate limiting para APIs
5. **Concorrência**: Não suporta execuções paralelas (SQLite single-threaded)

---

## 🐛 Reportar Problemas

Encontrou um bug? Crie uma issue com:

1. **Comando executado**
2. **Mensagem de erro completa**
3. **Versão do Python**: `python --version`
4. **Sistema operacional**: `uname -a` (Linux/Mac) ou `ver` (Windows)
5. **Arquivo .env** (sem credenciais!)
6. **Logs do Streamlit** (se aplicável)

---

## 👨‍💻 Autor

**Robson Marques**
Projeto experimental de automação de desenvolvimento ágil usando IA.

---

## 📜 Licença

Este projeto é experimental e educacional.

---

**Desenvolvido com:**
- 🤖 CrewAI Framework
- 🧠 Google Gemini 2.0 Flash Lite
- 🎨 Streamlit
- 🇧🇷 Português Brasileiro (pt-BR)

---

**Última atualização**: Outubro 2025
**Versão**: 1.0.0
