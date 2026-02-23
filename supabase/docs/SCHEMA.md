# Database Schema - Squad-AI

## Overview
- **Engine**: SQLite
- **File**: `demandas.db`

## Tables

### `demandas`
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key, Auto-increment |
| titulo | TEXT | Non-null |
| descricao | TEXT | Non-null |
| usar_jira | BOOLEAN | Default 0 |
| project_key | TEXT | |
| status | TEXT | Default 'pendente' |
| created_at | TIMESTAMP | Default CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | Default CURRENT_TIMESTAMP |
| executed_at | TIMESTAMP | |
| tags | TEXT | JSON string of tags |

### `resultados`
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key, Auto-increment |
| demanda_id | INTEGER | Foreign Key to `demandas.id` |
| agente | TEXT | Name of the agent |
| resultado | TEXT | Raw agent output |
| created_at | TIMESTAMP | Default CURRENT_TIMESTAMP |

## Indices
- `idx_demandas_status`: Index on `demandas(status)`
- `idx_demandas_created`: Index on `demandas(created_at DESC)`
- `idx_resultados_demanda`: Index on `resultados(demanda_id)`

## Identified Data Technical Debt
- **Schema Evolution**: No versioned migration system (e.g., Alembic). Schema is created via hardcoded strings in `database.py`.
- **Data Integrity**: JSON strings for `tags` instead of a separate table or formal JSON type (if supported).
- **Security**: No Row Level Security (RLS) equivalents; any system component with file access can read/write everything.
- **Scalability**: Standard SQLite file might experience lock issues if concurrent executions were implemented (currently sequential).
