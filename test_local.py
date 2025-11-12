#!/usr/bin/env python
"""
Teste local do Squad de Agentes - SEM integração Jira
Usa apenas Gemini para processamento local de demandas
"""

import sys
from pathlib import Path

# Adiciona o diretório src ao path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from dotenv import load_dotenv
load_dotenv()

print("\n" + "╔" + "═" * 68 + "╗")
print("║" + " " * 12 + "SQUAD DE AGENTES - TESTE LOCAL (SEM JIRA)" + " " * 14 + "║")
print("╚" + "═" * 68 + "╝\n")

print("🎯 Este teste executará o squad localmente sem integração Jira")
print("📝 Os agentes irão gerar especificações e código Python\n")

# Criação manual do crew sem usar decorators problemáticos
from crewai import Agent, Crew, Process, Task, LLM
from crewai_tools import FileReadTool

print("⚙️  Inicializando agentes...\n")

# LLM comum para todos os agentes
llm = LLM(
    model="gemini/gemini-2.0-flash-lite",
    temperature=0.7,
)

# Agente Analista de Sistemas (sem dependência de Jira)
analista = Agent(
    role="Analista de Sistemas",
    goal="Gerar especificação técnica clara e objetiva. Focar no essencial: objetivo, implementação, arquivo de destino, função principal, tratamento de erros e testes necessários.",
    backstory="""Você é um Analista de Sistemas experiente que foca no essencial,
    com habilidade para transformar requisitos em especificações técnicas detalhadas
    mas concisas. Você entende tanto o lado de negócio quanto o técnico.""",
    tools=[FileReadTool()],
    llm=llm,
    verbose=True,
    allow_delegation=False
)

# Agente Desenvolvedor Python
desenvolvedor = Agent(
    role="Desenvolvedor Python",
    goal="Gerar código Python funcional e sintaticamente válido com base na especificação técnica. Criar tanto o código principal quanto os testes unitários usando pytest.",
    backstory="""Você é um Desenvolvedor Python sênior com foco em qualidade de código.
    Você tem experiência em TDD e segue melhores práticas: type hints, tratamento de
    exceções, documentação clara e testes abrangentes. Seu código é sempre limpo,
    legível, sintaticamente correto e bem testado.""",
    llm=llm,
    verbose=True,
    allow_delegation=False
)

# Agente Quality Assurance (versão simplificada sem Jira)
qa = Agent(
    role="Quality Assurance",
    goal="Validar qualidade através de análise do código e testes. Garantir que o código atende aos requisitos técnicos.",
    backstory="""Você é um QA rigoroso mas pragmático, com experiência em testes.
    Você entende a importância de testes abrangentes mas sabe equilibrar qualidade
    com prazos. Você sempre documenta seus achados de forma clara.""",
    llm=llm,
    verbose=True,
    allow_delegation=False
)

print("✅ Agentes inicializados!\n")
print("📋 Definindo tarefas...\n")

# Definição de inputs
demanda_titulo = "Implementar função de validação de CPF"
demanda_descricao = """
Criar uma função Python que valide CPF brasileiro.

Requisitos:
- Aceitar CPF com ou sem formatação (123.456.789-00 ou 12345678900)
- Validar dígitos verificadores
- Retornar True para CPF válido, False para inválido
- Rejeitar CPFs com todos dígitos iguais (111.111.111-11)
- Incluir tratamento de erros para inputs inválidos

Critérios de aceite:
- Função deve validar corretamente CPFs válidos
- Função deve rejeitar CPFs inválidos
- Código deve ter testes unitários com pytest
"""

# Task 1: Gerar especificação técnica
task_especificacao = Task(
    description=f"""
    Gerar especificação técnica detalhada para a seguinte demanda:

    TÍTULO: {demanda_titulo}

    DESCRIÇÃO:
    {demanda_descricao}

    A especificação deve incluir:
    1. Objetivo da implementação
    2. Detalhes técnicos de implementação
    3. Nome do arquivo Python a ser criado
    4. Nome da função principal
    5. Parâmetros da função
    6. Tratamento de erros
    7. Casos de teste necessários

    Formato: Markdown claro e conciso
    """,
    expected_output="Especificação técnica em formato markdown com todos os detalhes de implementação",
    agent=analista
)

# Task 2: Desenvolver código Python
task_desenvolvimento = Task(
    description="""
    Com base na especificação técnica gerada, criar:

    1. Código Python principal com a implementação completa
    2. Testes unitários usando pytest

    Requisitos obrigatórios:
    - Type hints em todas as funções
    - Docstrings claras
    - Tratamento adequado de exceções
    - Testes cobrindo casos normais e excepcionais
    - Código deve seguir PEP 8

    IMPORTANTE: Apresente o código completo pronto para uso.
    """,
    expected_output="Código Python principal completo E arquivo de testes unitários completo",
    agent=desenvolvedor,
    context=[task_especificacao]
)

# Task 3: Validação de qualidade
task_validacao = Task(
    description="""
    Analisar o código Python gerado e validar:

    1. Qualidade do código (clareza, manutenibilidade)
    2. Presença de documentação adequada
    3. Tratamento de erros
    4. Cobertura de testes
    5. Aderência aos requisitos originais

    Gerar relatório completo com:
    - Checklist de qualidade
    - Problemas identificados (se houver)
    - Sugestões de melhoria (se aplicável)
    - Veredicto final: APROVADO ou PRECISA REVISÃO
    """,
    expected_output="Relatório de qualidade completo com análise detalhada e veredicto final",
    agent=qa,
    context=[task_desenvolvimento]
)

print("✅ Tarefas definidas!\n")
print("🚀 Criando crew...\n")

# Criar o crew
crew = Crew(
    agents=[analista, desenvolvedor, qa],
    tasks=[task_especificacao, task_desenvolvimento, task_validacao],
    process=Process.sequential,
    verbose=True
)

print("✅ Crew criado!\n")
print("=" * 70)
print("🎬 INICIANDO EXECUÇÃO DO SQUAD")
print("=" * 70)
print()
print("📊 Progresso:")
print("   1️⃣  Analista gerando especificação técnica...")
print("   2️⃣  Desenvolvedor criando código Python...")
print("   3️⃣  QA validando qualidade...")
print()
print("⏳ Aguarde... (isso pode levar alguns minutos)")
print("=" * 70)
print()

try:
    # Executar o crew
    result = crew.kickoff()

    print("\n" + "=" * 70)
    print("✅ EXECUÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 70)
    print()
    print("📄 RESULTADO FINAL:")
    print("=" * 70)
    print(result)
    print("=" * 70)

    # Salvar resultado em arquivo
    output_file = Path("output_teste_local.md")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# Resultado do Squad de Agentes - Teste Local\n\n")
        f.write(f"## Demanda\n\n")
        f.write(f"**Título:** {demanda_titulo}\n\n")
        f.write(f"**Descrição:**\n{demanda_descricao}\n\n")
        f.write(f"## Resultado da Execução\n\n")
        f.write(str(result))

    print(f"\n💾 Resultado salvo em: {output_file.absolute()}")
    print("\n🎉 Teste local concluído!")

except Exception as e:
    print("\n" + "=" * 70)
    print("❌ ERRO DURANTE EXECUÇÃO")
    print("=" * 70)
    print(f"\nErro: {str(e)}")
    print(f"\nTipo: {type(e).__name__}")

    import traceback
    print("\n📋 Traceback completo:")
    print("-" * 70)
    traceback.print_exc()
    print("-" * 70)

    sys.exit(1)
