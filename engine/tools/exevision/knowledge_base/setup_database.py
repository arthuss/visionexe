# setup_database.py (Version 4 - Advanced Database Setup mit Migration System)
import psycopg2
import os
import logging
from dotenv import load_dotenv
from contextlib import contextmanager
from typing import Optional, List, Dict
import sys

# Lade die Variablen aus der .env Datei
load_dotenv()

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('database_setup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Konfiguration
DB_CONFIG = {
    'host': os.getenv("DB_HOST"),
    'port': os.getenv("DB_PORT"),
    'dbname': os.getenv("DB_NAME"),
    'user': os.getenv("ADMIN_USER"),
    'password': os.getenv("ADMIN_PASSWORD")
}

AGENT_USER = os.getenv("AGENT_USER")
AGENT_PASSWORD = os.getenv("AGENT_PASSWORD")

# Datenbankschema-Version für Migrationen
CURRENT_SCHEMA_VERSION = 4

class DatabaseManager:
    def __init__(self, config: Dict):
        self.config = config
        
    @contextmanager
    def get_connection(self):
        """Context manager für sichere Datenbankverbindungen."""
        conn = None
        try:
            conn = psycopg2.connect(**self.config)
            conn.autocommit = True
            yield conn
        except psycopg2.Error as e:
            logger.error(f"Datenbankverbindungsfehler: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

    def execute_sql(self, conn, sql_command: str, params=None, description: str = ""):
        """Führt SQL-Befehle mit verbessertem Logging aus."""
        try:
            with conn.cursor() as cur:
                cur.execute(sql_command, params)
            
            log_msg = description or sql_command.strip().splitlines()[0][:70]
            logger.info(f"✅ {log_msg}")
            
        except psycopg2.Error as e:
            logger.error(f"❌ SQL-Fehler bei: {description or sql_command[:50]}...")
            logger.error(f"   Fehler: {e}")
            raise

    def create_schema_version_table(self, conn):
        """Erstellt Tabelle für Schema-Versionsverwaltung."""
        self.execute_sql(conn, """
            CREATE TABLE IF NOT EXISTS schema_versions (
                version INTEGER PRIMARY KEY,
                applied_at TIMESTAMPTZ DEFAULT NOW(),
                description TEXT
            );
        """, description="Schema-Versionstabelle erstellen")

    def get_current_version(self, conn) -> int:
        """Gibt die aktuelle Schema-Version zurück."""
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT MAX(version) FROM schema_versions;")
                result = cur.fetchone()
                return result[0] if result[0] is not None else 0
        except psycopg2.Error:
            return 0

    def apply_migration(self, conn, version: int, description: str, sql_commands: List[str]):
        """Wendet eine Migration an."""
        logger.info(f"🔄 Anwenden der Migration v{version}: {description}")
        
        for sql in sql_commands:
            self.execute_sql(conn, sql)
        
        # Version in Tabelle eintragen
        self.execute_sql(conn, 
            "INSERT INTO schema_versions (version, description) VALUES (%s, %s);",
            (version, description),
            f"Migration v{version} registrieren"
        )

    def setup_extensions(self, conn):
        """Installiert benötigte PostgreSQL-Erweiterungen."""
        extensions = [
            ("vector", "Vektor-Ähnlichkeitssuche"),
            ("uuid-ossp", "UUID-Generierung"),
            ("pg_trgm", "Textähnlichkeitssuche")
        ]
        
        for ext_name, description in extensions:
            try:
                self.execute_sql(conn, 
                    f"CREATE EXTENSION IF NOT EXISTS {ext_name};",
                    description=f"Erweiterung {ext_name} aktivieren"
                )
            except psycopg2.Error as e:
                logger.warning(f"⚠️  Erweiterung {ext_name} konnte nicht installiert werden: {e}")

    def create_initial_schema(self, conn):
        """Erstellt das initiale Datenbankschema (v1)."""
        migrations = [
            """CREATE TABLE IF NOT EXISTS api_documentation (
                doc_id SERIAL PRIMARY KEY,
                source_url TEXT,
                module TEXT,
                endpoint TEXT,
                method VARCHAR(10),
                content_chunk TEXT NOT NULL,
                content_embedding VECTOR(384),
                last_scraped_timestamp TIMESTAMPTZ DEFAULT NOW(),
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );""",
            
            """CREATE TABLE IF NOT EXISTS development_logs (
                log_id SERIAL PRIMARY KEY,
                timestamp TIMESTAMPTZ DEFAULT NOW(),
                source_file VARCHAR(255),
                topic VARCHAR(100),
                problem_summary TEXT,
                solution_summary TEXT,
                raw_chunk TEXT,
                content_embedding VECTOR(384),
                created_at TIMESTAMPTZ DEFAULT NOW()
            );""",
            
            """CREATE TABLE IF NOT EXISTS assets (
                asset_id VARCHAR(255) PRIMARY KEY,
                filename VARCHAR(255) NOT NULL,
                file_format VARCHAR(10),
                status VARCHAR(50) DEFAULT 'pending',
                llava_title TEXT,
                llava_description TEXT,
                main_llm_description TEXT,
                internal_category VARCHAR(100),
                tags JSONB DEFAULT '[]'::jsonb,
                platform_categories JSONB DEFAULT '{}'::jsonb,
                description_embedding VECTOR(384),
                last_processed_timestamp TIMESTAMPTZ,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );""",
            
            """CREATE TABLE IF NOT EXISTS renderings (
                rendering_id SERIAL PRIMARY KEY,
                asset_id VARCHAR(255) REFERENCES assets(asset_id) ON DELETE CASCADE,
                image_name VARCHAR(255) NOT NULL,
                angle INT DEFAULT 0,
                image_embedding VECTOR(512),
                created_at TIMESTAMPTZ DEFAULT NOW()
            );"""
        ]
        
        self.apply_migration(conn, 1, "Initiales Schema", migrations)

    def create_indexes(self, conn):
        """Erstellt Performance-Indizes (v2)."""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_api_docs_embedding ON api_documentation USING ivfflat (content_embedding vector_cosine_ops);",
            "CREATE INDEX IF NOT EXISTS idx_dev_logs_embedding ON development_logs USING ivfflat (content_embedding vector_cosine_ops);",
            "CREATE INDEX IF NOT EXISTS idx_assets_embedding ON assets USING ivfflat (description_embedding vector_cosine_ops);",
            "CREATE INDEX IF NOT EXISTS idx_renderings_embedding ON renderings USING ivfflat (image_embedding vector_cosine_ops);",
            "CREATE INDEX IF NOT EXISTS idx_assets_status ON assets(status);",
            "CREATE INDEX IF NOT EXISTS idx_assets_category ON assets(internal_category);",
            "CREATE INDEX IF NOT EXISTS idx_api_docs_module ON api_documentation(module);",
            "CREATE INDEX IF NOT EXISTS idx_dev_logs_topic ON development_logs(topic);",
            "CREATE INDEX IF NOT EXISTS idx_assets_filename ON assets USING gin(filename gin_trgm_ops);"
        ]
        
        self.apply_migration(conn, 2, "Performance-Indizes", indexes)

    def add_audit_triggers(self, conn):
        """Fügt Audit-Trigger für updated_at hinzu (v3)."""
        audit_function = """
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        """
        
        triggers = [
            audit_function,
            "CREATE TRIGGER update_assets_updated_at BEFORE UPDATE ON assets FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();",
            "CREATE TRIGGER update_api_docs_updated_at BEFORE UPDATE ON api_documentation FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();"
        ]
        
        self.apply_migration(conn, 3, "Audit-Trigger", triggers)

    def add_advanced_features(self, conn):
        """Fügt erweiterte Features hinzu (v4)."""
        advanced_features = [
            """CREATE TABLE IF NOT EXISTS search_analytics (
                search_id SERIAL PRIMARY KEY,
                query_text TEXT NOT NULL,
                query_embedding VECTOR(384),
                result_count INTEGER,
                execution_time_ms INTEGER,
                user_session VARCHAR(255),
                created_at TIMESTAMPTZ DEFAULT NOW()
            );""",
            
            """CREATE TABLE IF NOT EXISTS asset_relationships (
                relationship_id SERIAL PRIMARY KEY,
                source_asset_id VARCHAR(255) REFERENCES assets(asset_id) ON DELETE CASCADE,
                target_asset_id VARCHAR(255) REFERENCES assets(asset_id) ON DELETE CASCADE,
                relationship_type VARCHAR(50) NOT NULL,
                confidence_score FLOAT DEFAULT 0.0,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                UNIQUE(source_asset_id, target_asset_id, relationship_type)
            );""",
            
            "CREATE INDEX IF NOT EXISTS idx_search_analytics_embedding ON search_analytics USING ivfflat (query_embedding vector_cosine_ops);",
            "CREATE INDEX IF NOT EXISTS idx_asset_relationships_source ON asset_relationships(source_asset_id);",
            "CREATE INDEX IF NOT EXISTS idx_asset_relationships_target ON asset_relationships(target_asset_id);"
        ]
        
        self.apply_migration(conn, 4, "Erweiterte Features", advanced_features)

    def setup_user_permissions(self, conn):
        """Richtet Benutzerberechtigungen ein."""
        logger.info("🔐 Richte Benutzerberechtigungen ein...")
        
        with conn.cursor() as cur:
            # Prüfe ob User existiert
            cur.execute("SELECT 1 FROM pg_roles WHERE rolname=%s", (AGENT_USER,))
            user_exists = cur.fetchone() is not None
            
            if not user_exists:
                self.execute_sql(conn, 
                    f"CREATE ROLE {AGENT_USER} LOGIN PASSWORD %s;",
                    (AGENT_PASSWORD,),
                    f"Benutzer {AGENT_USER} erstellen"
                )
            else:
                self.execute_sql(conn, 
                    f"ALTER ROLE {AGENT_USER} PASSWORD %s;",
                    (AGENT_PASSWORD,),
                    f"Passwort für {AGENT_USER} aktualisieren"
                )
        
        # Berechtigungen setzen
        permissions = [
            f"GRANT CONNECT ON DATABASE {DB_CONFIG['dbname']} TO {AGENT_USER};",
            f"GRANT USAGE ON SCHEMA public TO {AGENT_USER};",
            f"GRANT SELECT ON ALL TABLES IN SCHEMA public TO {AGENT_USER};",
            f"GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO {AGENT_USER};"
        ]
        
        for perm in permissions:
            self.execute_sql(conn, perm, description="Berechtigung setzen")

    def setup_database(self):
        """Hauptfunktion für Datenbanksetup mit Migrationssystem."""
        logger.info("🚀 Starte Datenbanksetup...")
        
        with self.get_connection() as conn:
            # Schema-Versionstabelle erstellen
            self.create_schema_version_table(conn)
            current_version = self.get_current_version(conn)
            
            logger.info(f"📊 Aktuelle Schema-Version: {current_version}")
            logger.info(f"🎯 Ziel-Version: {CURRENT_SCHEMA_VERSION}")
            
            # Erweiterungen installieren
            self.setup_extensions(conn)
            
            # Migrationen anwenden
            if current_version < 1:
                self.create_initial_schema(conn)
            
            if current_version < 2:
                self.create_indexes(conn)
            
            if current_version < 3:
                self.add_audit_triggers(conn)
            
            if current_version < 4:
                self.add_advanced_features(conn)
            
            # Benutzerberechtigungen
            self.setup_user_permissions(conn)
            
            logger.info("✅ Datenbanksetup erfolgreich abgeschlossen!")

def main():
    """Hauptfunktion."""
    # Validiere Konfiguration
    missing_vars = [k for k, v in DB_CONFIG.items() if not v]
    if missing_vars or not AGENT_USER or not AGENT_PASSWORD:
        logger.error(f"❌ Fehlende Umgebungsvariablen: {missing_vars}")
        sys.exit(1)
    
    try:
        db_manager = DatabaseManager(DB_CONFIG)
        db_manager.setup_database()
    except Exception as e:
        logger.error(f"❌ Setup fehlgeschlagen: {e}")
        raise

if __name__ == "__main__":
    main()