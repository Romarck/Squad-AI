"""
Módulo de execução do crew com tracking de progresso
Para uso com a interface web Streamlit
"""

from crewai import Agent, Crew, Process, Task, LLM
from crewai_tools import FileReadTool
from typing import Dict, Callable, Optional
import os
import time


def executar_crew_com_tracking(
    demanda_titulo: str,
    demanda_descricao: str,
    usar_jira: bool = False,
    project_key: str = "LOCAL",
    progress_callback: Optional[Callable] = None
) -> Dict[str, str]:
    """
    Executa o crew com tracking de progresso para interface web.

    Args:
        demanda_titulo: Título da demanda
        demanda_descricao: Descrição detalhada
        usar_jira: Se deve usar integração Jira
        project_key: Chave do projeto Jira
        progress_callback: Função de callback para atualizar progresso
                          callback(step: int, agent_name: str, message: str)

    Returns:
        Dict com resultados de cada agente
    """

    def log_progress(step: int, agent_name: str, message: str):
        """Helper para logging de progresso"""
        if progress_callback:
            progress_callback(step, agent_name, message)
        print(f"[Step {step}] {agent_name}: {message}")

    resultados = {}

    # LLM comum
    llm = LLM(
        model="gemini/gemini-2.5-flash",
        temperature=0.7,
        api_key=os.getenv("GEMINI_API_KEY")
    )

    # =========================================================================
    # ETAPA 1: PRODUCT OWNER
    # =========================================================================
    log_progress(1, "Product Owner", "Iniciando análise da demanda...")

    if usar_jira:
        # Versão com Jira
        from squad_de_agentes_inteligentes___mvp_desenvolvimento_agil.tools.jira_integration_tool import JiraIntegrationTool
        from squad_de_agentes_inteligentes___mvp_desenvolvimento_agil.tools.jira_connectivity_tester import JiraConnectivityTesterTool

        po = Agent(
            role="Product Owner",
            goal=f"Testar conectividade Jira e criar user story estruturada para {demanda_titulo} no projeto {project_key}",
            backstory="""Você é um Product Owner experiente focado em clareza e simplicidade.
            Transforma demandas em user stories bem estruturadas no Jira.""",
            tools=[JiraIntegrationTool(), JiraConnectivityTesterTool()],
            llm=llm,
            verbose=False,
            allow_delegation=False
        )

        task_po = Task(
            description=f"""
            1. Testar conectividade com Jira para o projeto {project_key}
            2. Criar user story estruturada no Jira:
               - Título: {demanda_titulo}
               - Descrição: {demanda_descricao}
               - 2-3 critérios de aceitação claros
            """,
            expected_output="Issue criada no Jira com key (ex: PROJ-123) e critérios de aceitação",
            agent=po
        )
    else:
        # Versão sem Jira (local)
        po = Agent(
            role="Product Owner",
            goal=f"Estruturar user story detalhada para {demanda_titulo}",
            backstory="""Você é um Product Owner experiente focado em clareza e simplicidade.
            Transforma demandas em user stories bem estruturadas.""",
            llm=llm,
            verbose=False,
            allow_delegation=False
        )

        task_po = Task(
            description=f"""
            Criar user story estruturada:

            TÍTULO: {demanda_titulo}

            DESCRIÇÃO:
            {demanda_descricao}

            Formate a user story com:
            1. Resumo executivo
            2. Detalhamento funcional
            3. 2-3 critérios de aceitação claros e mensuráveis

            Formato: Markdown
            """,
            expected_output="User story formatada em markdown com critérios de aceitação claros",
            agent=po
        )

    log_progress(1, "Product Owner", "Processando demanda...")

    # Executar PO
    crew_po = Crew(
        agents=[po],
        tasks=[task_po],
        process=Process.sequential,
        verbose=False
    )

    resultado_po = str(crew_po.kickoff())
    resultados["Product Owner"] = resultado_po
    log_progress(1, "Product Owner", "✅ User story criada!")

    # =========================================================================
    # ETAPA 2: ANALISTA DE SISTEMAS
    # =========================================================================
    log_progress(2, "Analista de Sistemas", "Analisando requisitos...")

    analista = Agent(
        role="Analista de Sistemas",
        goal="Gerar especificação técnica clara e objetiva com foco no essencial",
        backstory="""Você é um Analista de Sistemas experiente que transforma
        user stories em especificações técnicas detalhadas mas concisas.""",
        tools=[FileReadTool()],
        llm=llm,
        verbose=False,
        allow_delegation=False
    )

    task_analista = Task(
        description=f"""
        Com base na user story a seguir, gerar especificação técnica completa:

        {resultado_po}

        A especificação deve incluir:
        1. Objetivo da implementação
        2. Detalhes técnicos de implementação
        3. Nome do arquivo Python
        4. Nome da função principal
        5. Parâmetros e tipos
        6. Tratamento de erros
        7. Casos de teste necessários

        Formato: Markdown estruturado
        """,
        expected_output="Especificação técnica em markdown com todos os detalhes de implementação",
        agent=analista
    )

    log_progress(2, "Analista de Sistemas", "Gerando especificação técnica...")

    crew_analista = Crew(
        agents=[analista],
        tasks=[task_analista],
        process=Process.sequential,
        verbose=False
    )

    resultado_analista = str(crew_analista.kickoff())
    resultados["Analista de Sistemas"] = resultado_analista
    log_progress(2, "Analista de Sistemas", "✅ Especificação técnica gerada!")

    # =========================================================================
    # ETAPA 3: DESENVOLVEDOR PYTHON
    # =========================================================================
    log_progress(3, "Desenvolvedor Python", "Iniciando desenvolvimento...")

    desenvolvedor = Agent(
        role="Desenvolvedor Python",
        goal="Criar código Python funcional e sintaticamente válido com testes unitários",
        backstory="""Você é um Desenvolvedor Python sênior com foco em qualidade.
        Segue melhores práticas: type hints, docstrings, tratamento de erros e testes abrangentes.""",
        llm=llm,
        verbose=False,
        allow_delegation=False
    )

    task_dev = Task(
        description=f"""
        Com base na especificação técnica, criar:

        ESPECIFICAÇÃO:
        {resultado_analista}

        Entregar:
        1. Código Python principal completo
        2. Testes unitários usando pytest

        Requisitos obrigatórios:
        - Type hints em todas as funções
        - Docstrings detalhadas
        - Tratamento adequado de exceções
        - Testes cobrindo casos normais e excepcionais
        - Código seguindo PEP 8

        IMPORTANTE: Apresente TODO o código pronto para uso, separado em blocos de código.
        """,
        expected_output="Código Python completo E testes unitários completos, ambos prontos para uso",
        agent=desenvolvedor
    )

    log_progress(3, "Desenvolvedor Python", "Implementando código e testes...")

    crew_dev = Crew(
        agents=[desenvolvedor],
        tasks=[task_dev],
        process=Process.sequential,
        verbose=False
    )

    resultado_dev = str(crew_dev.kickoff())
    resultados["Desenvolvedor Python"] = resultado_dev
    log_progress(3, "Desenvolvedor Python", "✅ Código e testes implementados!")

    # =========================================================================
    # ETAPA 4: QUALITY ASSURANCE
    # =========================================================================
    log_progress(4, "Quality Assurance", "Iniciando validação...")

    qa = Agent(
        role="Quality Assurance",
        goal="Validar qualidade do código através de análise detalhada",
        backstory="""Você é um QA rigoroso mas pragmático com experiência em testes.
        Documenta achados de forma clara e mantém rastreabilidade.""",
        llm=llm,
        verbose=False,
        allow_delegation=False
    )

    if usar_jira:
        from squad_de_agentes_inteligentes___mvp_desenvolvimento_agil.tools.jira_integration_tool import JiraIntegrationTool
        qa.tools = [JiraIntegrationTool()]

        task_qa_desc = f"""
        Analisar o código gerado e atualizar Jira:

        CÓDIGO GERADO:
        {resultado_dev}

        1. Validar qualidade do código
        2. Verificar tratamento de erros
        3. Analisar cobertura de testes
        4. Gerar relatório completo
        5. Atualizar issue Jira com os resultados

        Relatório deve conter:
        - Checklist de qualidade
        - Problemas identificados
        - Sugestões de melhoria
        - Veredicto final: APROVADO ou PRECISA REVISÃO
        """
    else:
        task_qa_desc = f"""
        Analisar o código gerado:

        CÓDIGO GERADO:
        {resultado_dev}

        Validar:
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
        """

    task_qa = Task(
        description=task_qa_desc,
        expected_output="Relatório de qualidade completo com análise detalhada e veredicto final",
        agent=qa
    )

    log_progress(4, "Quality Assurance", "Executando análise de qualidade...")

    crew_qa = Crew(
        agents=[qa],
        tasks=[task_qa],
        process=Process.sequential,
        verbose=False
    )

    resultado_qa = str(crew_qa.kickoff())
    resultados["Quality Assurance"] = resultado_qa
    log_progress(4, "Quality Assurance", "✅ Validação concluída!")

    # =========================================================================
    # FINALIZAÇÃO
    # =========================================================================
    log_progress(4, "Sistema", "🎉 Execução completa!")

    return resultados
