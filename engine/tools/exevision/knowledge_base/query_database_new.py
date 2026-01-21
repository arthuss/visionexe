# query_database.py (Version 3 - Enhanced User Interface)
import psycopg2
from sentence_transformers import SentenceTransformer
import numpy as np
import os
import sys
from dotenv import load_dotenv
from typing import List, Tuple, Optional
import time

# Lade die Variablen aus der .env Datei
load_dotenv()

# --- KONFIGURATION ---
DB_CONFIG = {
    'host': os.getenv("DB_HOST"),
    'port': os.getenv("DB_PORT"),
    'dbname': os.getenv("DB_NAME"),
    'user': os.getenv("AGENT_USER"),
    'password': os.getenv("AGENT_PASSWORD")
}

EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'
DEFAULT_TOP_K = 5

class KnowledgeBaseQuery:
    """Erweiterte Suchfunktionalität für die Knowledge Base."""
    
    def __init__(self):
        self.model = None
        self.connection = None
        self.load_model()
        
    def load_model(self):
        """Lädt das Embedding-Modell."""
        print("🤖 Lade Embedding-Modell... (kann einen Moment dauern)")
        try:
            self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)
            print("✅ Modell erfolgreich geladen!")
        except Exception as e:
            print(f"❌ Fehler beim Laden des Modells: {e}")
            sys.exit(1)

    def create_connection(self):
        """Stellt eine Verbindung zur Datenbank her."""
        try:
            self.connection = psycopg2.connect(**DB_CONFIG)
            return True
        except psycopg2.OperationalError as e:
            print(f"\n❌ Datenbankverbindung fehlgeschlagen!")
            print("💡 Stelle sicher, dass:")
            print("   - Docker-Container läuft (start_knowledge_base.bat)")
            print("   - .env-Datei korrekt konfiguriert ist")
            print(f"\nDetails: {e}")
            return False

    def search_assets(self, query_text: str, limit: int = DEFAULT_TOP_K) -> List[Tuple]:
        """Sucht in Assets mit Vektor-Ähnlichkeit."""
        if not query_text.strip():
            return []
            
        print(f"\n🔍 Suche nach: '{query_text}'")
        start_time = time.time()
        
        # Erstelle Embedding
        query_embedding = self.model.encode(query_text)
        
        # SQL-Abfrage
        sql = """
        SELECT 
            asset_id, 
            llava_title, 
            main_llm_description,
            internal_category,
            tags,
            description_embedding <=> %s::vector AS distance
        FROM assets
        WHERE description_embedding IS NOT NULL
        ORDER BY distance
        LIMIT %s;
        """
        
        try:
            with self.connection.cursor() as cur:
                cur.execute(sql, (query_embedding.tolist(), limit))
                results = cur.fetchall()
                
                # Speichere Suchstatistik
                self.log_search(query_text, query_embedding, len(results), 
                              int((time.time() - start_time) * 1000))
                
                return results
        except Exception as e:
            print(f"❌ Suchfehler: {e}")
            return []

    def search_api_docs(self, query_text: str, limit: int = DEFAULT_TOP_K) -> List[Tuple]:
        """Sucht in API-Dokumentation."""
        if not query_text.strip():
            return []
            
        query_embedding = self.model.encode(query_text)
        
        sql = """
        SELECT 
            module,
            endpoint,
            method,
            content_chunk,
            content_embedding <=> %s::vector AS distance
        FROM api_documentation
        WHERE content_embedding IS NOT NULL
        ORDER BY distance
        LIMIT %s;
        """
        
        try:
            with self.connection.cursor() as cur:
                cur.execute(sql, (query_embedding.tolist(), limit))
                return cur.fetchall()
        except Exception as e:
            print(f"❌ API-Suchfehler: {e}")
            return []

    def search_dev_logs(self, query_text: str, limit: int = DEFAULT_TOP_K) -> List[Tuple]:
        """Sucht in Development Logs."""
        if not query_text.strip():
            return []
            
        query_embedding = self.model.encode(query_text)
        
        sql = """
        SELECT 
            topic,
            problem_summary,
            solution_summary,
            source_file,
            content_embedding <=> %s::vector AS distance
        FROM development_logs
        WHERE content_embedding IS NOT NULL
        ORDER BY distance
        LIMIT %s;
        """
        
        try:
            with self.connection.cursor() as cur:
                cur.execute(sql, (query_embedding.tolist(), limit))
                return cur.fetchall()
        except Exception as e:
            print(f"❌ Dev-Log-Suchfehler: {e}")
            return []

    def log_search(self, query_text: str, query_embedding: np.ndarray, 
                   result_count: int, execution_time_ms: int):
        """Protokolliert Suchvorgänge für Analytics."""
        try:
            sql = """
            INSERT INTO search_analytics 
            (query_text, query_embedding, result_count, execution_time_ms, user_session)
            VALUES (%s, %s, %s, %s, %s);
            """
            with self.connection.cursor() as cur:
                cur.execute(sql, (
                    query_text, 
                    query_embedding.tolist(),
                    result_count,
                    execution_time_ms,
                    f"session_{int(time.time())}"
                ))
                self.connection.commit()
        except Exception:
            # Ignoriere Logging-Fehler
            pass

    def display_asset_results(self, results: List[Tuple], query: str):
        """Zeigt Asset-Suchergebnisse formatiert an."""
        if not results:
            print("😔 Keine Assets gefunden.")
            return
            
        print(f"\n📦 ASSET-ERGEBNISSE für '{query}':")
        print("=" * 80)
        
        for i, (asset_id, title, description, category, tags, distance) in enumerate(results, 1):
            similarity = (1 - distance) * 100
            
            print(f"\n{i}. 🎯 {asset_id} (Ähnlichkeit: {similarity:.1f}%)")
            print(f"   📋 Titel: {title or 'N/A'}")
            print(f"   🏷️  Kategorie: {category or 'N/A'}")
            
            # Beschreibung kürzen
            if description:
                desc_short = description[:150] + "..." if len(description) > 150 else description
                print(f"   📝 Beschreibung: {desc_short}")
            
            # Tags anzeigen
            if tags and tags != '[]':
                try:
                    import json
                    tag_list = json.loads(tags) if isinstance(tags, str) else tags
                    if tag_list:
                        print(f"   🏷️  Tags: {', '.join(tag_list[:5])}")
                except:
                    pass
            
            print("-" * 80)

    def display_api_results(self, results: List[Tuple], query: str):
        """Zeigt API-Dokumentation-Ergebnisse an."""
        if not results:
            print("😔 Keine API-Dokumentation gefunden.")
            return
            
        print(f"\n📚 API-DOKUMENTATION für '{query}':")
        print("=" * 80)
        
        for i, (module, endpoint, method, content, distance) in enumerate(results, 1):
            similarity = (1 - distance) * 100
            
            print(f"\n{i}. 🔗 {module} - {endpoint} (Ähnlichkeit: {similarity:.1f}%)")
            print(f"   🌐 Method: {method or 'N/A'}")
            
            if content:
                content_short = content[:200] + "..." if len(content) > 200 else content
                print(f"   📄 Inhalt: {content_short}")
            
            print("-" * 80)

    def display_dev_log_results(self, results: List[Tuple], query: str):
        """Zeigt Development-Log-Ergebnisse an."""
        if not results:
            print("😔 Keine Development Logs gefunden.")
            return
            
        print(f"\n📝 DEVELOPMENT LOGS für '{query}':")
        print("=" * 80)
        
        for i, (topic, problem, solution, source_file, distance) in enumerate(results, 1):
            similarity = (1 - distance) * 100
            
            print(f"\n{i}. 🐛 {topic or 'N/A'} (Ähnlichkeit: {similarity:.1f}%)")
            print(f"   📁 Datei: {source_file or 'N/A'}")
            
            if problem:
                problem_short = problem[:150] + "..." if len(problem) > 150 else problem
                print(f"   ❓ Problem: {problem_short}")
                
            if solution:
                solution_short = solution[:150] + "..." if len(solution) > 150 else solution
                print(f"   ✅ Lösung: {solution_short}")
            
            print("-" * 80)

    def show_main_menu(self):
        """Zeigt das Hauptsuchmenü."""
        print("\n" + "="*60)
        print("🔍 KI KNOWLEDGE BASE - SUCHE")
        print("="*60)
        print("1. 📦 In Assets suchen")
        print("2. 📚 In API-Dokumentation suchen")
        print("3. 📝 In Development Logs suchen")
        print("4. 🌟 Überall suchen")
        print("5. 📊 Such-Statistiken anzeigen")
        print("6. ❌ Beenden")
        print("="*60)

    def search_everywhere(self, query_text: str, limit: int = 3):
        """Sucht in allen verfügbaren Datenquellen."""
        print(f"\n🌟 UNIVERSELLE SUCHE: '{query_text}'")
        
        # Assets durchsuchen
        asset_results = self.search_assets(query_text, limit)
        if asset_results:
            self.display_asset_results(asset_results, query_text)
        
        # API-Docs durchsuchen
        api_results = self.search_api_docs(query_text, limit)
        if api_results:
            self.display_api_results(api_results, query_text)
        
        # Dev-Logs durchsuchen
        dev_results = self.search_dev_logs(query_text, limit)
        if dev_results:
            self.display_dev_log_results(dev_results, query_text)
        
        total_results = len(asset_results) + len(api_results) + len(dev_results)
        if total_results == 0:
            print("\n😔 Keine Ergebnisse in der gesamten Knowledge Base gefunden.")

    def show_search_stats(self):
        """Zeigt Suchstatistiken an."""
        try:
            with self.connection.cursor() as cur:
                # Häufigste Suchanfragen
                cur.execute("""
                    SELECT query_text, COUNT(*) as search_count
                    FROM search_analytics
                    GROUP BY query_text
                    ORDER BY search_count DESC
                    LIMIT 10;
                """)
                top_queries = cur.fetchall()
                
                # Durchschnittliche Ausführungszeit
                cur.execute("SELECT AVG(execution_time_ms) FROM search_analytics;")
                avg_time = cur.fetchone()[0]
                
                print("\n📊 SUCH-STATISTIKEN:")
                print("-" * 50)
                print(f"⏱️  Durchschnittliche Suchzeit: {avg_time:.1f}ms" if avg_time else "⏱️  Noch keine Daten")
                
                if top_queries:
                    print("\n🔥 Häufigste Suchanfragen:")
                    for i, (query, count) in enumerate(top_queries, 1):
                        print(f"   {i}. '{query}' ({count}x)")
                
        except Exception as e:
            print(f"❌ Fehler beim Abrufen der Statistiken: {e}")

    def run(self):
        """Hauptschleife der Anwendung."""
        print("🔍 Knowledge Base Query Interface gestartet...")
        
        if not self.create_connection():
            return
            
        print("✅ Datenbankverbindung hergestellt!")
        
        while True:
            try:
                self.show_main_menu()
                choice = input("\nWähle eine Option (1-6): ").strip()
                
                if choice == "1":
                    query = input("\n📦 Asset-Suche - Eingabe: ").strip()
                    if query:
                        results = self.search_assets(query)
                        self.display_asset_results(results, query)
                        
                elif choice == "2":
                    query = input("\n📚 API-Suche - Eingabe: ").strip()
                    if query:
                        results = self.search_api_docs(query)
                        self.display_api_results(results, query)
                        
                elif choice == "3":
                    query = input("\n📝 Dev-Log-Suche - Eingabe: ").strip()
                    if query:
                        results = self.search_dev_logs(query)
                        self.display_dev_log_results(results, query)
                        
                elif choice == "4":
                    query = input("\n🌟 Universelle Suche - Eingabe: ").strip()
                    if query:
                        self.search_everywhere(query)
                        
                elif choice == "5":
                    self.show_search_stats()
                    
                elif choice == "6":
                    print("\n👋 Auf Wiedersehen!")
                    break
                    
                else:
                    print("❌ Ungültige Auswahl!")
                    
                if choice in ["1", "2", "3", "4", "5"]:
                    input("\nDrücke Enter um fortzufahren...")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Programm beendet.")
                break
            except Exception as e:
                print(f"\n❌ Unerwarteter Fehler: {e}")
                input("Drücke Enter um fortzufahren...")
        
        if self.connection:
            self.connection.close()

def main():
    """Hauptfunktion."""
    query_interface = KnowledgeBaseQuery()
    query_interface.run()

if __name__ == "__main__":
    main()
