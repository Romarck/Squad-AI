"""
Sistema de banco de dados para histórico de demandas
SQLite com CRUD completo
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import json


class DemandaDB:
    """Gerenciador de banco de dados de demandas"""

    def __init__(self, db_path: str = "demandas.db"):
        """
        Inicializa o banco de dados.

        Args:
            db_path: Caminho para o arquivo do banco de dados
        """
        self.db_path = db_path
        self._criar_tabelas()

    def _get_connection(self):
        """Retorna uma conexão com o banco de dados"""
        return sqlite3.connect(self.db_path)

    def _criar_tabelas(self):
        """Cria as tabelas necessárias no banco de dados"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Tabela de demandas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS demandas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                descricao TEXT NOT NULL,
                usar_jira BOOLEAN DEFAULT 0,
                project_key TEXT,
                status TEXT DEFAULT 'pendente',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                executed_at TIMESTAMP,
                tags TEXT
            )
        """)

        # Tabela de resultados
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resultados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                demanda_id INTEGER NOT NULL,
                agente TEXT NOT NULL,
                resultado TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (demanda_id) REFERENCES demandas (id)
            )
        """)

        # Índices para performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_demandas_status
            ON demandas(status)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_demandas_created
            ON demandas(created_at DESC)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_resultados_demanda
            ON resultados(demanda_id)
        """)

        conn.commit()
        conn.close()

    # =========================================================================
    # CREATE
    # =========================================================================

    def criar_demanda(
        self,
        titulo: str,
        descricao: str,
        usar_jira: bool = False,
        project_key: str = "LOCAL",
        tags: List[str] = None
    ) -> int:
        """
        Cria uma nova demanda no banco de dados.

        Args:
            titulo: Título da demanda
            descricao: Descrição detalhada
            usar_jira: Se deve usar integração Jira
            project_key: Chave do projeto Jira
            tags: Lista de tags para categorização

        Returns:
            ID da demanda criada
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        tags_str = json.dumps(tags) if tags else "[]"

        cursor.execute("""
            INSERT INTO demandas
            (titulo, descricao, usar_jira, project_key, tags)
            VALUES (?, ?, ?, ?, ?)
        """, (titulo, descricao, usar_jira, project_key, tags_str))

        demanda_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return demanda_id

    def salvar_resultado(
        self,
        demanda_id: int,
        agente: str,
        resultado: str
    ):
        """
        Salva o resultado de um agente para uma demanda.

        Args:
            demanda_id: ID da demanda
            agente: Nome do agente
            resultado: Resultado gerado pelo agente
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO resultados (demanda_id, agente, resultado)
            VALUES (?, ?, ?)
        """, (demanda_id, agente, resultado))

        conn.commit()
        conn.close()

    # =========================================================================
    # READ
    # =========================================================================

    def listar_demandas(
        self,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """
        Lista demandas com filtros opcionais.

        Args:
            status: Filtrar por status (pendente, executando, concluida, erro)
            limit: Número máximo de resultados
            offset: Offset para paginação

        Returns:
            Lista de demandas como dicionários
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        if status:
            cursor.execute("""
                SELECT * FROM demandas
                WHERE status = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (status, limit, offset))
        else:
            cursor.execute("""
                SELECT * FROM demandas
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))

        columns = [desc[0] for desc in cursor.description]
        demandas = []

        for row in cursor.fetchall():
            demanda = dict(zip(columns, row))
            # Converter tags de JSON para lista
            demanda['tags'] = json.loads(demanda.get('tags', '[]'))
            demandas.append(demanda)

        conn.close()
        return demandas

    def obter_demanda(self, demanda_id: int) -> Optional[Dict]:
        """
        Obtém uma demanda específica por ID.

        Args:
            demanda_id: ID da demanda

        Returns:
            Dicionário com dados da demanda ou None se não encontrada
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM demandas WHERE id = ?", (demanda_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return None

        columns = [desc[0] for desc in cursor.description]
        demanda = dict(zip(columns, row))
        demanda['tags'] = json.loads(demanda.get('tags', '[]'))

        conn.close()
        return demanda

    def obter_resultados(self, demanda_id: int) -> Dict[str, str]:
        """
        Obtém todos os resultados de uma demanda.

        Args:
            demanda_id: ID da demanda

        Returns:
            Dicionário {agente: resultado}
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT agente, resultado
            FROM resultados
            WHERE demanda_id = ?
            ORDER BY created_at ASC
        """, (demanda_id,))

        resultados = {}
        for agente, resultado in cursor.fetchall():
            resultados[agente] = resultado

        conn.close()
        return resultados

    def pesquisar_demandas(self, termo: str, limit: int = 50) -> List[Dict]:
        """
        Pesquisa demandas por termo no título ou descrição.

        Args:
            termo: Termo de pesquisa
            limit: Número máximo de resultados

        Returns:
            Lista de demandas encontradas
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM demandas
            WHERE titulo LIKE ? OR descricao LIKE ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (f"%{termo}%", f"%{termo}%", limit))

        columns = [desc[0] for desc in cursor.description]
        demandas = []

        for row in cursor.fetchall():
            demanda = dict(zip(columns, row))
            demanda['tags'] = json.loads(demanda.get('tags', '[]'))
            demandas.append(demanda)

        conn.close()
        return demandas

    # =========================================================================
    # UPDATE
    # =========================================================================

    def atualizar_demanda(
        self,
        demanda_id: int,
        titulo: Optional[str] = None,
        descricao: Optional[str] = None,
        usar_jira: Optional[bool] = None,
        project_key: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """
        Atualiza uma demanda existente.

        Args:
            demanda_id: ID da demanda
            titulo: Novo título (opcional)
            descricao: Nova descrição (opcional)
            usar_jira: Novo valor para usar_jira (opcional)
            project_key: Nova chave de projeto (opcional)
            tags: Novas tags (opcional)

        Returns:
            True se atualizado com sucesso, False caso contrário
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Construir query dinamicamente
        updates = []
        params = []

        if titulo is not None:
            updates.append("titulo = ?")
            params.append(titulo)

        if descricao is not None:
            updates.append("descricao = ?")
            params.append(descricao)

        if usar_jira is not None:
            updates.append("usar_jira = ?")
            params.append(usar_jira)

        if project_key is not None:
            updates.append("project_key = ?")
            params.append(project_key)

        if tags is not None:
            updates.append("tags = ?")
            params.append(json.dumps(tags))

        if not updates:
            conn.close()
            return False

        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(demanda_id)

        query = f"UPDATE demandas SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)

        success = cursor.rowcount > 0
        conn.commit()
        conn.close()

        return success

    def atualizar_status(
        self,
        demanda_id: int,
        status: str,
        marcar_executada: bool = False
    ) -> bool:
        """
        Atualiza o status de uma demanda.

        Args:
            demanda_id: ID da demanda
            status: Novo status (pendente, executando, concluida, erro)
            marcar_executada: Se True, atualiza executed_at

        Returns:
            True se atualizado com sucesso
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        if marcar_executada:
            cursor.execute("""
                UPDATE demandas
                SET status = ?, executed_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status, demanda_id))
        else:
            cursor.execute("""
                UPDATE demandas
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status, demanda_id))

        success = cursor.rowcount > 0
        conn.commit()
        conn.close()

        return success

    # =========================================================================
    # DELETE
    # =========================================================================

    def deletar_demanda(self, demanda_id: int) -> bool:
        """
        Deleta uma demanda e seus resultados.

        Args:
            demanda_id: ID da demanda

        Returns:
            True se deletado com sucesso
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Deletar resultados primeiro (chave estrangeira)
        cursor.execute("DELETE FROM resultados WHERE demanda_id = ?", (demanda_id,))

        # Deletar demanda
        cursor.execute("DELETE FROM demandas WHERE id = ?", (demanda_id,))

        success = cursor.rowcount > 0
        conn.commit()
        conn.close()

        return success

    # =========================================================================
    # ESTATÍSTICAS
    # =========================================================================

    def obter_estatisticas(self) -> Dict:
        """
        Obtém estatísticas gerais do banco de dados.

        Returns:
            Dicionário com estatísticas
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        stats = {}

        # Total de demandas
        cursor.execute("SELECT COUNT(*) FROM demandas")
        stats['total_demandas'] = cursor.fetchone()[0]

        # Por status
        cursor.execute("""
            SELECT status, COUNT(*)
            FROM demandas
            GROUP BY status
        """)
        stats['por_status'] = dict(cursor.fetchall())

        # Total executadas
        cursor.execute("SELECT COUNT(*) FROM demandas WHERE executed_at IS NOT NULL")
        stats['total_executadas'] = cursor.fetchone()[0]

        # Última execução
        cursor.execute("""
            SELECT executed_at
            FROM demandas
            WHERE executed_at IS NOT NULL
            ORDER BY executed_at DESC
            LIMIT 1
        """)
        result = cursor.fetchone()
        stats['ultima_execucao'] = result[0] if result else None

        conn.close()
        return stats


# Instância singleton
_db_instance = None


def get_db() -> DemandaDB:
    """Retorna instância singleton do banco de dados"""
    global _db_instance
    if _db_instance is None:
        _db_instance = DemandaDB()
    return _db_instance
