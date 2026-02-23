# System Architecture - Squad-AI

## Technical Stack
- **Backend**: Python 3.10+
- **Agent Framework**: CrewAI >= 0.203.0
- **UI Framework**: Streamlit
- **Database**: SQLite (via standard library/SQLAlchemy)
- **Environment Management**: .env files
- **Tooling**: 
    - `crewai[tools]`
    - `python-dotenv`
    - `SQLAlchemy`
    - `streamlit`

## Folder Structure
- `/`: Entry points (`app_completo.py`, `main.py`, `database.py`)
- `src/squad_de_agentes_inteligentes___mvp_desenvolvimento_agil/`: Core logic
    - `config/`: Agents and Tasks YAML definitions
    - `tools/`: Custom agents tools
    - `crew.py`: Crew configuration and agent/task definitions
    - `crew_runner.py`: Streamlit integration for tracking execution

## Architecture Patterns
- **MAS (Multi-Agent System)**: Sequential pipeline of 4 agents.
- **Singleton Database**: `database.py` utilizes a singleton pattern for `DemandaDB`.
- **Streamlit Session State**: Heavy reliance on `st.session_state` for frontend-backend communication and history management.

## Identified System Technical Debt
- **Dependency Management**: `pyproject.toml` lists only `crewai[tools]`. Transitive dependencies (Streamlit, SQLAlchemy) are not explicitly managed in the primary manifest.
- **Testing**: Complete absence of a `tests/` directory or unit tests for core logic.
- **Error Handling**: Basic try/except blocks in `app_completo.py` which may mask deep failures.
- **Documentation**: Missing high-level technical documentation for developers.
