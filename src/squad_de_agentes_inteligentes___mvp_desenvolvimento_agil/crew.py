import os

from crewai import LLM
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import (
	FileReadTool
)
from squad_de_agentes_inteligentes___mvp_desenvolvimento_agil.tools.jira_integration_tool import JiraIntegrationTool
from squad_de_agentes_inteligentes___mvp_desenvolvimento_agil.tools.pytest_execution_simulator import PytestExecutionSimulator
from squad_de_agentes_inteligentes___mvp_desenvolvimento_agil.tools.jira_connectivity_tester import JiraConnectivityTesterTool





@CrewBase
class SquadDeAgentesInteligentesMvpDesenvolvimentoAgilCrew:
    """SquadDeAgentesInteligentesMvpDesenvolvimentoAgil crew"""

    
    @agent
    def product_owner(self) -> Agent:


        return Agent(
            config=self.agents_config["product_owner"],


            tools=[
				JiraIntegrationTool(),
				JiraConnectivityTesterTool()
            ],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            max_execution_time=None,
            llm=LLM(
                model="gemini/gemini-2.5-flash",
                temperature=0.7,
                api_key=os.getenv("GEMINI_API_KEY")
            ),
            language="pt-BR",

        )
    
    @agent
    def desenvolvedor_python(self) -> Agent:


        return Agent(
            config=self.agents_config["desenvolvedor_python"],


            tools=[
				PytestExecutionSimulator(),
				FileReadTool()
            ],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            max_execution_time=None,
            llm=LLM(
                model="gemini/gemini-2.5-flash",
                temperature=0.7,
                api_key=os.getenv("GEMINI_API_KEY")
            ),
            language="pt-BR",

        )
    
    @agent
    def quality_assurance(self) -> Agent:


        return Agent(
            config=self.agents_config["quality_assurance"],


            tools=[
				PytestExecutionSimulator(),
				JiraIntegrationTool(),
				JiraConnectivityTesterTool()
            ],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            max_execution_time=None,
            llm=LLM(
                model="gemini/gemini-2.5-flash",
                temperature=0.7,
                api_key=os.getenv("GEMINI_API_KEY")
            ),
            language="pt-BR",

        )
    
    @agent
    def analista_de_sistemas(self) -> Agent:


        return Agent(
            config=self.agents_config["analista_de_sistemas"],


            tools=[
				FileReadTool()
            ],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            max_execution_time=None,
            llm=LLM(
                model="gemini/gemini-2.5-flash",
                temperature=0.7,
                api_key=os.getenv("GEMINI_API_KEY")
            ),
            language="pt-BR",

        )
    

    
    @task
    def criar_user_story_no_jira(self) -> Task:
        return Task(
            config=self.tasks_config["criar_user_story_no_jira"],
            markdown=False,
            
            
        )
    
    @task
    def gerar_especificacao_tecnica(self) -> Task:
        return Task(
            config=self.tasks_config["gerar_especificacao_tecnica"],
            markdown=False,
            
            
        )
    
    @task
    def desenvolver_codigo_python(self) -> Task:
        return Task(
            config=self.tasks_config["desenvolver_codigo_python"],
            markdown=False,
            
            
        )
    
    @task
    def executar_testes_e_validacao_final(self) -> Task:
        return Task(
            config=self.tasks_config["executar_testes_e_validacao_final"],
            markdown=False,
            
            
        )
    

    @crew
    def crew(self) -> Crew:
        """Creates the SquadDeAgentesInteligentesMvpDesenvolvimentoAgil crew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )

    def _load_response_format(self, name):
        with open(os.path.join(self.base_directory, "config", f"{name}.json")) as f:
            json_schema = json.loads(f.read())

        return SchemaConverter.build(json_schema)
