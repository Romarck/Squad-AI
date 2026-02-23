import pytest
import os
import shutil
from database import DemandaDB

def test_db_connection():
    # Testar se o singleton do banco inicializa sem erros
    db = DemandaDB()
    assert db is not None
    assert os.path.exists("demandas.db")

def test_db_obter_demandas():
    db = DemandaDB()
    demandas = db.listar_demandas(limit=1)
    # Deve retornar uma lista (mesmo que vazia se o banco estiver novo)
    assert isinstance(demandas, list)

def test_backup_manager():
    from utils.backup_manager import BackupManager
    bm = BackupManager(db_path="demandas.db", backup_dir="test_backups")
    backup_path = bm.criar_backup()
    assert os.path.exists(backup_path)
    # Cleanup
    shutil.rmtree("test_backups")

def test_crew_import():
    try:
        from squad_de_agentes_inteligentes___mvp_desenvolvimento_agil.crew import SquadDeAgentesInteligentesMvpDesenvolvimentoAgilCrew
        crew = SquadDeAgentesInteligentesMvpDesenvolvimentoAgilCrew().crew()
        assert crew is not None
    except Exception as e:
        pytest.fail(f"Erro ao importar ou inicializar Crew: {e}")
