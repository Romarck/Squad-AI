#!/usr/bin/env python
"""
Script de validação de configuração para Squad de Agentes Inteligentes.
Verifica se todas as variáveis de ambiente necessárias estão configuradas
e testa conectividade com APIs externas.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth


def print_header(title):
    """Imprime cabeçalho formatado."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_status(message, status="info"):
    """Imprime mensagem com status."""
    symbols = {
        "success": "✅",
        "error": "❌",
        "warning": "⚠️ ",
        "info": "ℹ️ "
    }
    print(f"{symbols.get(status, 'ℹ️ ')} {message}")


def check_env_file():
    """Verifica se o arquivo .env existe."""
    print_header("1. Verificando arquivo .env")

    env_path = Path(".env")
    env_example_path = Path(".env.example")

    if not env_path.exists():
        print_status("Arquivo .env não encontrado!", "error")
        if env_example_path.exists():
            print_status("Arquivo .env.example encontrado", "info")
            print("\n📝 Execute o seguinte comando para criar o .env:")
            print("   cp .env.example .env")
            print("\n   Depois edite o .env com suas credenciais.")
        else:
            print_status("Arquivo .env.example também não encontrado!", "error")
        return False

    print_status("Arquivo .env encontrado", "success")
    return True


def check_environment_variables():
    """Verifica se todas as variáveis necessárias estão configuradas."""
    print_header("2. Verificando variáveis de ambiente")

    # Carrega .env
    load_dotenv()

    required_vars = {
        "GEMINI_API_KEY": "Google Gemini API Key",
        "JIRA_URL": "URL da instância Jira",
        "JIRA_EMAIL": "Email do usuário Jira",
        "JIRA_API_KEY": "API Token do Jira"
    }

    optional_vars = {
        "HTTP_PROXY": "Proxy HTTP (opcional)",
        "HTTPS_PROXY": "Proxy HTTPS (opcional)"
    }

    all_ok = True

    # Verifica variáveis obrigatórias
    print("\n📋 Variáveis obrigatórias:")
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value or value.strip() == "" or "your_" in value or "example" in value:
            print_status(f"{var} ({description}): NÃO CONFIGURADA", "error")
            all_ok = False
        else:
            # Mascara valores sensíveis
            masked_value = value[:8] + "..." if len(value) > 8 else "***"
            print_status(f"{var} ({description}): {masked_value}", "success")

    # Verifica variáveis opcionais
    print("\n📋 Variáveis opcionais:")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value and value.strip():
            print_status(f"{var} ({description}): Configurado", "success")
        else:
            print_status(f"{var} ({description}): Não configurado (OK)", "info")

    return all_ok


def test_gemini_api():
    """Testa conectividade com Google Gemini API."""
    print_header("3. Testando Google Gemini API")

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key or "your_" in api_key:
        print_status("GEMINI_API_KEY não configurada, pulando teste", "warning")
        return False

    try:
        # Testa endpoint de modelos disponíveis
        url = f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            models = response.json().get("models", [])
            print_status(f"Conectado com sucesso! {len(models)} modelos disponíveis", "success")

            # Lista alguns modelos
            gemini_models = [m for m in models if "gemini" in m.get("name", "").lower()]
            if gemini_models:
                print("\n   Modelos Gemini disponíveis:")
                for model in gemini_models[:5]:
                    model_name = model.get("name", "").split("/")[-1]
                    print(f"     • {model_name}")
            return True
        elif response.status_code == 401:
            print_status("Autenticação falhou - verifique sua API Key", "error")
            return False
        elif response.status_code == 403:
            print_status("Acesso negado - verifique permissões da API Key", "error")
            return False
        else:
            print_status(f"Erro HTTP {response.status_code}: {response.text[:100]}", "error")
            return False

    except requests.exceptions.Timeout:
        print_status("Timeout ao conectar com Gemini API", "error")
        return False
    except requests.exceptions.RequestException as e:
        print_status(f"Erro de conexão: {str(e)}", "error")
        return False
    except Exception as e:
        print_status(f"Erro inesperado: {str(e)}", "error")
        return False


def test_jira_connection():
    """Testa conectividade com Jira."""
    print_header("4. Testando conectividade Jira")

    jira_url = os.getenv("JIRA_URL")
    jira_email = os.getenv("JIRA_EMAIL")
    jira_api_key = os.getenv("JIRA_API_KEY")

    if not all([jira_url, jira_email, jira_api_key]) or "your_" in jira_email:
        print_status("Credenciais Jira não configuradas, pulando teste", "warning")
        return False

    try:
        # Normaliza URL
        jira_url = jira_url.rstrip('/')

        # Testa autenticação com endpoint /myself
        url = f"{jira_url}/rest/api/3/myself"
        auth = HTTPBasicAuth(jira_email, jira_api_key)
        headers = {"Accept": "application/json"}

        print_status(f"Testando conexão com {jira_url}...", "info")

        response = requests.get(url, auth=auth, headers=headers, timeout=30)

        if response.status_code == 200:
            user_data = response.json()
            display_name = user_data.get("displayName", "Desconhecido")
            email = user_data.get("emailAddress", "N/A")
            account_id = user_data.get("accountId", "N/A")

            print_status(f"Autenticação bem-sucedida!", "success")
            print(f"\n   👤 Usuário: {display_name}")
            print(f"   📧 Email: {email}")
            print(f"   🆔 Account ID: {account_id}")

            # Testa listagem de projetos
            projects_url = f"{jira_url}/rest/api/3/project"
            projects_response = requests.get(projects_url, auth=auth, headers=headers, timeout=30)

            if projects_response.status_code == 200:
                projects = projects_response.json()
                print_status(f"Encontrados {len(projects)} projetos acessíveis", "success")

                if projects:
                    print("\n   📁 Projetos disponíveis:")
                    for project in projects[:5]:
                        key = project.get("key", "?")
                        name = project.get("name", "?")
                        project_type = project.get("projectTypeKey", "?")
                        print(f"     • {key}: {name} (Tipo: {project_type})")

                    if len(projects) > 5:
                        print(f"     ... e mais {len(projects) - 5} projetos")
                else:
                    print_status("Nenhum projeto acessível encontrado", "warning")

            return True

        elif response.status_code == 401:
            print_status("Autenticação falhou - verifique email e API token", "error")
            return False
        elif response.status_code == 403:
            print_status("Acesso negado - verifique permissões", "error")
            return False
        elif response.status_code == 404:
            print_status("URL Jira inválida ou endpoint não encontrado", "error")
            return False
        else:
            print_status(f"Erro HTTP {response.status_code}: {response.text[:200]}", "error")
            return False

    except requests.exceptions.Timeout:
        print_status("Timeout ao conectar com Jira (30s)", "error")
        return False
    except requests.exceptions.ConnectionError:
        print_status("Erro de conexão - verifique URL e conectividade", "error")
        return False
    except requests.exceptions.RequestException as e:
        print_status(f"Erro de requisição: {str(e)}", "error")
        return False
    except Exception as e:
        print_status(f"Erro inesperado: {str(e)}", "error")
        return False


def check_python_version():
    """Verifica versão do Python."""
    print_header("0. Verificando ambiente Python")

    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    print_status(f"Python {version_str}", "info")

    if version.major == 3 and 10 <= version.minor < 14:
        print_status("Versão do Python compatível (>= 3.10, < 3.14)", "success")
        return True
    else:
        print_status("Versão do Python incompatível! Requer Python >= 3.10 e < 3.14", "error")
        return False


def check_dependencies():
    """Verifica se dependências estão instaladas."""
    print_header("5. Verificando dependências")

    required_packages = [
        ("crewai", "CrewAI framework"),
        ("requests", "HTTP requests"),
        ("pydantic", "Data validation"),
        ("python-dotenv", "Environment variables")
    ]

    all_installed = True

    for package, description in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print_status(f"{package} ({description}): Instalado", "success")
        except ImportError:
            print_status(f"{package} ({description}): NÃO INSTALADO", "error")
            all_installed = False

    if not all_installed:
        print("\n📦 Para instalar dependências faltantes, execute:")
        print("   pip install crewai[tools] python-dotenv")
        print("   ou: crewai install")

    return all_installed


def print_summary(results):
    """Imprime resumo da validação."""
    print_header("📊 RESUMO DA VALIDAÇÃO")

    total = len(results)
    passed = sum(1 for r in results.values() if r)

    print(f"\nTestes executados: {total}")
    print(f"Testes bem-sucedidos: {passed}")
    print(f"Testes com problemas: {total - passed}")

    if passed == total:
        print("\n" + "🎉" * 10)
        print("\n✅ TUDO PRONTO! Você pode executar o crew:")
        print("\n   python main.py run")
        print("   ou: crewai run")
        print("\n" + "🎉" * 10)
        return True
    else:
        print("\n" + "⚠️ " * 10)
        print("\n❌ CONFIGURAÇÃO INCOMPLETA!")
        print("\nResolva os problemas acima antes de executar o crew.")
        print("\n📖 Consulte README.md para instruções detalhadas.")
        print("\n" + "⚠️ " * 10)
        return False


def main():
    """Função principal."""
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 10 + "VALIDADOR DE CONFIGURAÇÃO - SQUAD DE AGENTES" + " " * 13 + "║")
    print("╚" + "═" * 68 + "╝")

    results = {}

    # Executa validações
    results["python_version"] = check_python_version()
    results["env_file"] = check_env_file()

    if results["env_file"]:
        results["env_vars"] = check_environment_variables()
        results["dependencies"] = check_dependencies()
        results["gemini"] = test_gemini_api()
        results["jira"] = test_jira_connection()
    else:
        print("\n⏭️  Pulando testes de conectividade (arquivo .env não encontrado)")
        results["env_vars"] = False
        results["dependencies"] = False
        results["gemini"] = False
        results["jira"] = False

    # Resumo
    all_ok = print_summary(results)

    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
