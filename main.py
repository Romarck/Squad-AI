#!/usr/bin/env python
"""
Squad de Agentes Inteligentes - MVP Desenvolvimento Ágil
Entry point principal para execução do crew.
"""
import sys
import os
from pathlib import Path

# Adiciona o diretório src ao path para imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from squad_de_agentes_inteligentes___mvp_desenvolvimento_agil.main import run, train, replay, test


def print_usage():
    """Imprime instruções de uso."""
    print("""
TPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW
Q  Squad de Agentes Inteligentes - MVP Desenvolvimento Ágil       Q
ZPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP]

USO:
  python main.py <comando> [argumentos]

COMANDOS:
  run     - Executa o crew com inputs interativos ou via CLI
  train   - Treina o crew (requer: <iterations> <filename>)
  replay  - Repete execução de uma task (requer: <task_id>)
  test    - Testa o crew (requer: <iterations> <model_name>)

EXEMPLOS:
  python main.py run
  python main.py train 5 training_data.pkl
  python main.py replay task_123
  python main.py test 3 gpt-4

CONFIGURAÇÃO:
  1. Copie .env.example para .env
  2. Configure suas credenciais (GEMINI_API_KEY, JIRA_*)
  3. Execute: python main.py run

DOCUMENTAÇÃO:
  Veja README_PT.md para instruções detalhadas
""")


def main():
    """Função principal."""
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(0)

    command = sys.argv[1].lower()

    # Remove o nome do comando dos argumentos
    sys.argv.pop(1)

    if command == "run":
        run()
    elif command == "train":
        train()
    elif command == "replay":
        replay()
    elif command == "test":
        test()
    elif command in ["-h", "--help", "help"]:
        print_usage()
    else:
        print(f"L Comando desconhecido: {command}\n")
        print_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
