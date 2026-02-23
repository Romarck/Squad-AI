import shutil
import os
from datetime import datetime

class BackupManager:
    """Gerencia backups do banco de dados SQLite."""
    
    def __init__(self, db_path: str = "demandas.db", backup_dir: str = "backups"):
        self.db_path = db_path
        self.backup_dir = backup_dir
        
        # Garantir que o diretório de backup existe
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            
    def criar_backup(self) -> str:
        """
        Cria uma cópia binária do banco de dados.
        Retorna o caminho do arquivo de backup criado.
        """
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Banco de dados não encontrado em: {self.db_path}")
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_{timestamp}.db"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        try:
            shutil.copy2(self.db_path, backup_path)
            print(f"✅ Backup criado com sucesso: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"❌ Erro ao criar backup: {e}")
            raise e
            
    def limpar_backups_antigos(self, manter_ultimos: int = 5):
        """Mantém apenas os N backups mais recentes."""
        backups = sorted(
            [f for f in os.listdir(self.backup_dir) if f.startswith("backup_") and f.endswith(".db")],
            key=lambda x: os.path.getctime(os.path.join(self.backup_dir, x)),
            reverse=True
        )
        
        for backup_velho in backups[manter_ultimos:]:
            os.remove(os.path.join(self.backup_dir, backup_velho))
            print(f"🗑️ Backup antigo removido: {backup_velho}")
