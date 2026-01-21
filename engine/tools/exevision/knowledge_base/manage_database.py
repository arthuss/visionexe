# manage_database.py - Zentrales Management-Tool für die KI Knowledge Base
import os
import sys
import logging
from typing import Dict, List
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
from contextlib import contextmanager

# Lade Umgebungsvariablen
load_dotenv()

class KnowledgeBaseManager:
    """Zentrales Management-Tool für die KI Knowledge Base."""
    
    def __init__(self):
        self.config = {
            'host': os.getenv("DB_HOST"),
            'port': os.getenv("DB_PORT"),
            'dbname': os.getenv("DB_NAME"),
            'user': os.getenv("ADMIN_USER"),
            'password': os.getenv("ADMIN_PASSWORD")
        }
        self.setup_logging()
        
    def setup_logging(self):
        """Konfiguriert das Logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('kb_manager.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    @contextmanager
    def get_connection(self):
        """Sichere Datenbankverbindung."""
        conn = None
        try:
            conn = psycopg2.connect(**self.config)
            yield conn
        except psycopg2.Error as e:
            self.logger.error(f"Datenbankfehler: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def show_main_menu(self):
        """Zeigt das Hauptmenü."""
        print("\n" + "="*60)
        print("🧠 KI KNOWLEDGE BASE MANAGER")
        print("="*60)
        print("1. 📊 Datenbank-Status anzeigen")
        print("2. 🔧 Datenbank einrichten/aktualisieren")
        print("3. 📥 Daten importieren")
        print("4. 🔍 Datenbank durchsuchen")
        print("5. 👥 Benutzer verwalten")
        print("6. 📈 Statistiken anzeigen")
        print("7. 🛠️  Wartung")
        print("8. ❌ Beenden")
        print("="*60)

    def show_database_status(self):
        """Zeigt den aktuellen Datenbankstatus."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # Schema-Version prüfen
                    try:
                        cur.execute("SELECT MAX(version) FROM schema_versions;")
                        version = cur.fetchone()[0] or 0
                    except:
                        version = 0
                    
                    # Tabellen-Status
                    tables_info = []
                    table_names = ['assets', 'api_documentation', 'development_logs', 'renderings', 'search_analytics']
                    
                    for table in table_names:
                        try:
                            cur.execute(f"SELECT COUNT(*) FROM {table};")
                            count = cur.fetchone()[0]
                            tables_info.append((table, count, "✅"))
                        except:
                            tables_info.append((table, 0, "❌"))
                    
                    print("\n📊 DATENBANK-STATUS")
                    print("-" * 50)
                    print(f"Schema-Version: {version}")
                    print(f"Verbindung: ✅ {self.config['host']}:{self.config['port']}")
                    print("\nTabellen:")
                    for table, count, status in tables_info:
                        print(f"  {status} {table:<20} {count:>10} Einträge")
                        
        except Exception as e:
            print(f"❌ Fehler beim Abrufen des Status: {e}")

    def setup_database(self):
        """Startet das Datenbank-Setup."""
        print("\n🔧 DATENBANK-SETUP")
        print("-" * 50)
        try:
            from setup_database import DatabaseManager
            db_manager = DatabaseManager(self.config)
            db_manager.setup_database()
        except Exception as e:
            print(f"❌ Setup fehlgeschlagen: {e}")

    def import_menu(self):
        """Zeigt das Import-Menü."""
        print("\n📥 DATEN-IMPORT")
        print("-" * 50)
        print("1. Assets aus CSV importieren")
        print("2. API-Dokumentation importieren")
        print("3. Development Logs importieren")
        print("4. Zurück zum Hauptmenü")
        
        choice = input("\nWähle eine Option: ").strip()
        
        if choice == "1":
            self.import_assets()
        elif choice == "2":
            self.import_api_docs()
        elif choice == "3":
            self.import_dev_logs()

    def import_assets(self):
        """Importiert Assets."""
        try:
            from ingest_assets import main as ingest_assets_main
            ingest_assets_main()
        except Exception as e:
            print(f"❌ Asset-Import fehlgeschlagen: {e}")

    def import_api_docs(self):
        """Importiert API-Dokumentation."""
        print("🚧 API-Import wird implementiert...")
        # TODO: Implementierung der API-Dokumentation-Import

    def import_dev_logs(self):
        """Importiert Development Logs."""
        print("🚧 Dev-Log-Import wird implementiert...")
        # TODO: Implementierung des Development-Log-Imports

    def search_database(self):
        """Startet die Datenbanksuche."""
        try:
            from query_database import main as query_main
            query_main()
        except Exception as e:
            print(f"❌ Suche fehlgeschlagen: {e}")

    def manage_users(self):
        """Benutzerverwaltung."""
        print("\n👥 BENUTZERVERWALTUNG")
        print("-" * 50)
        print("1. Alle Benutzer anzeigen")
        print("2. Neuen Benutzer erstellen")
        print("3. Benutzer-Berechtigungen ändern")
        print("4. Zurück")
        
        choice = input("\nWähle eine Option: ").strip()
        
        if choice == "1":
            self.show_users()
        elif choice == "2":
            self.create_user()
        elif choice == "3":
            self.modify_user_permissions()

    def show_users(self):
        """Zeigt alle Datenbankbenutzer."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT rolname, rolcanlogin, rolcreatedb, rolsuper 
                        FROM pg_roles 
                        WHERE rolname NOT LIKE 'pg_%' 
                        ORDER BY rolname;
                    """)
                    users = cur.fetchall()
                    
                    print("\n👥 DATENBANKBENUTZER:")
                    print("-" * 60)
                    print(f"{'Name':<15} {'Login':<8} {'CreateDB':<10} {'Superuser':<10}")
                    print("-" * 60)
                    for name, login, createdb, super_user in users:
                        login_str = "✅" if login else "❌"
                        createdb_str = "✅" if createdb else "❌"
                        super_str = "✅" if super_user else "❌"
                        print(f"{name:<15} {login_str:<8} {createdb_str:<10} {super_str:<10}")
                        
        except Exception as e:
            print(f"❌ Fehler beim Abrufen der Benutzer: {e}")

    def create_user(self):
        """Erstellt einen neuen Benutzer."""
        username = input("Benutzername: ").strip()
        password = input("Passwort: ").strip()
        
        if not username or not password:
            print("❌ Benutzername und Passwort sind erforderlich!")
            return
            
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(f"CREATE ROLE {username} LOGIN PASSWORD %s;", (password,))
                    cur.execute(f"GRANT CONNECT ON DATABASE {self.config['dbname']} TO {username};")
                    cur.execute(f"GRANT USAGE ON SCHEMA public TO {username};")
                    cur.execute(f"GRANT SELECT ON ALL TABLES IN SCHEMA public TO {username};")
                    print(f"✅ Benutzer '{username}' erfolgreich erstellt!")
                    
        except Exception as e:
            print(f"❌ Fehler beim Erstellen des Benutzers: {e}")

    def show_statistics(self):
        """Zeigt Datenbankstatistiken."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    stats = {}
                    
                    # Asset-Statistiken
                    cur.execute("SELECT COUNT(*) FROM assets;")
                    stats['total_assets'] = cur.fetchone()[0]
                    
                    cur.execute("SELECT COUNT(DISTINCT internal_category) FROM assets WHERE internal_category IS NOT NULL;")
                    stats['asset_categories'] = cur.fetchone()[0]
                    
                    # API-Dokumentation
                    cur.execute("SELECT COUNT(*) FROM api_documentation;")
                    stats['api_docs'] = cur.fetchone()[0]
                    
                    # Development Logs
                    cur.execute("SELECT COUNT(*) FROM development_logs;")
                    stats['dev_logs'] = cur.fetchone()[0]
                    
                    # Suchstatistiken
                    try:
                        cur.execute("SELECT COUNT(*) FROM search_analytics;")
                        stats['searches'] = cur.fetchone()[0]
                    except:
                        stats['searches'] = 0
                    
                    print("\n📈 DATENBANK-STATISTIKEN")
                    print("-" * 50)
                    print(f"📦 Assets gesamt:        {stats['total_assets']:>10}")
                    print(f"🏷️  Asset-Kategorien:     {stats['asset_categories']:>10}")
                    print(f"📚 API-Dokumentationen:  {stats['api_docs']:>10}")
                    print(f"📝 Development Logs:     {stats['dev_logs']:>10}")
                    print(f"🔍 Durchgeführte Suchen: {stats['searches']:>10}")
                    
        except Exception as e:
            print(f"❌ Fehler beim Abrufen der Statistiken: {e}")

    def maintenance_menu(self):
        """Wartungsmenü."""
        print("\n🛠️  WARTUNG")
        print("-" * 50)
        print("1. Datenbankgröße anzeigen")
        print("2. Index-Status prüfen")
        print("3. Backup erstellen")
        print("4. Logs bereinigen")
        print("5. Zurück")
        
        choice = input("\nWähle eine Option: ").strip()
        
        if choice == "1":
            self.show_database_size()
        elif choice == "2":
            self.check_indexes()
        elif choice == "3":
            self.create_backup()
        elif choice == "4":
            self.cleanup_logs()

    def show_database_size(self):
        """Zeigt die Datenbankgröße."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT pg_size_pretty(pg_database_size(current_database()));")
                    db_size = cur.fetchone()[0]
                    print(f"\n💾 Datenbankgröße: {db_size}")
                    
        except Exception as e:
            print(f"❌ Fehler beim Abrufen der Datenbankgröße: {e}")

    def run(self):
        """Hauptschleife des Managers."""
        print("🧠 KI Knowledge Base Manager gestartet...")
        
        while True:
            try:
                self.show_main_menu()
                choice = input("\nWähle eine Option (1-8): ").strip()
                
                if choice == "1":
                    self.show_database_status()
                elif choice == "2":
                    self.setup_database()
                elif choice == "3":
                    self.import_menu()
                elif choice == "4":
                    self.search_database()
                elif choice == "5":
                    self.manage_users()
                elif choice == "6":
                    self.show_statistics()
                elif choice == "7":
                    self.maintenance_menu()
                elif choice == "8":
                    print("\n👋 Auf Wiedersehen!")
                    break
                else:
                    print("❌ Ungültige Auswahl!")
                    
                input("\nDrücke Enter um fortzufahren...")
                
            except KeyboardInterrupt:
                print("\n\n👋 Programm beendet.")
                break
            except Exception as e:
                print(f"\n❌ Unerwarteter Fehler: {e}")
                input("Drücke Enter um fortzufahren...")

def main():
    """Hauptfunktion."""
    manager = KnowledgeBaseManager()
    manager.run()

if __name__ == "__main__":
    main()
