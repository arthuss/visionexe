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

# ... (Der Rest der Datei bleibt exakt gleich) ...
def create_connection():
    """Stellt eine Verbindung zur Datenbank mit dem Agenten-Benutzer her."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST, port=DB_PORT, dbname=DB_NAME, 
            user=AGENT_USER, password=AGENT_PASSWORD
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"\nFATAL: Konnte keine Verbindung zur Datenbank herstellen.")
        print("Stelle sicher, dass der Docker-Container läuft (start_database.bat).")
        print(f"Details: {e}")
        return None

def search_assets(conn, model, query_text):
    """
    Erstellt ein Embedding für die Suchanfrage und führt eine Vektor-Suche durch.
    """
    if not query_text:
        return    print("\nErstelle Embedding für die Suchanfrage...")
    query_embedding = model.encode(query_text)

    print(f"Suche nach den {TOP_K_RESULTS} ähnlichsten Assets...")
    
    sql_search = f"""
    SELECT 
        asset_id, 
        llava_title, 
        main_llm_description,
        internal_category,
        description_embedding <=> %s::vector AS distance
    FROM 
        assets
    ORDER BY 
        distance
    LIMIT %s;
    """
    
    results = []
    try:
        with conn.cursor() as cur:
            cur.execute(sql_search, (query_embedding.tolist(), TOP_K_RESULTS))
            results = cur.fetchall()
    except Exception as e:
        print(f"Fehler bei der Datenbankabfrage: {e}")
        return

    print("-" * 70)
    if not results:
        print("Keine Ergebnisse gefunden.")
    else:
        print(f"Top {len(results)} Ergebnisse für: '{query_text}'\n")
        for i, row in enumerate(results):
            asset_id, title, desc, category, distance = row
            print(f"  {i+1}. Asset: {asset_id} (Ähnlichkeit: {1 - distance:.2f})")
            print(f"     Titel: {title}")
            print(f"     Kategorie: {category}")
            # Kürze die Beschreibung für die Anzeige
            desc_short = (desc[:120] + '...') if desc and len(desc) > 120 else desc
            print(f"     Beschreibung: {desc_short}\n")
    print("-" * 70)

if __name__ == "__main__":
    print("Lade Such-Modell... (kann einen Moment dauern)")
    embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    print("Modell geladen.")
    
    db_connection = create_connection()
    if db_connection:
        print("\n--- Interaktive Asset-Suche ---")
        print("Gib deine Suchanfrage ein oder tippe 'exit' zum Beenden.")
        
        while True:
            query = input("\nSuche > ")
            if query.lower() == 'exit':
                break
            search_assets(db_connection, embedding_model, query)
            
        db_connection.close()
        print("\nProgramm beendet. Datenbankverbindung geschlossen.")