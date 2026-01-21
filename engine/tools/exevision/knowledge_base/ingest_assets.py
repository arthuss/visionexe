# ingest_assets.py (Version 3 - mit .env)
import psycopg2
import pandas as pd
from sentence_transformers import SentenceTransformer
import numpy as np
import json
import os
from dotenv import load_dotenv

# Lade die Variablen aus der .env Datei
load_dotenv()

# --- KONFIGURATION (wird jetzt aus der .env Datei geladen) ---
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
ADMIN_USER = os.getenv("ADMIN_USER")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

CSV_FILE_PATH = r"C:\Users\Public\Documents\Assets\converted_blends\batch_summary_llava.csv"
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'

# ... (Der Rest der Datei bleibt exakt gleich) ...

def create_connection():
    """Stellt eine Verbindung zur Datenbank her."""
    try:
        conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=ADMIN_USER, password=ADMIN_PASSWORD)
        return conn
    except psycopg2.Error as e:
        print(f"Fehler bei der Datenbankverbindung: {e}")
        return None

def clean_and_validate_json(data, default_if_invalid='{}'):
    """
    Bereinigt und validiert einen String, um sicherzustellen, dass er gültiges JSON ist.
    Fängt NaN, None und andere ungültige Werte ab.
    """
    if pd.isna(data):
        return default_if_invalid
    if isinstance(data, (dict, list)):
        return json.dumps(data) # Wenn es schon ein Python-Objekt ist, direkt umwandeln
    if isinstance(data, str):
        # Entferne führende/nachfolgende Leerzeichen
        data = data.strip()
        # Prüfe auf gültige JSON-Strukturen
        if (data.startswith('{') and data.endswith('}')) or \
           (data.startswith('[') and data.endswith(']')):
            try:
                # Versuche, es zu parsen, um die Gültigkeit zu bestätigen
                json.loads(data)
                return data
            except json.JSONDecodeError:
                return default_if_invalid
    # Wenn alles andere fehlschlägt, gib den Standardwert zurück
    return default_if_invalid


def ingest_assets_from_csv(conn, model):
    """Liest die CSV, erstellt Embeddings und schreibt die Daten in die DB."""
    try:
        df = pd.read_csv(CSV_FILE_PATH)
        # Ersetze alle NaN-Werte in der gesamten DataFrame durch None (einfacher zu handhaben)
        df = df.where(pd.notna(df), None)
        print(f"{len(df)} Zeilen aus '{os.path.basename(CSV_FILE_PATH)}' geladen.")
    except FileNotFoundError:
        print(f"FEHLER: Die CSV-Datei wurde nicht unter '{CSV_FILE_PATH}' gefunden.")
        return

    upserted_count = 0
    with conn.cursor() as cur:
        for index, row in df.iterrows():
            # 1. Asset ID extrahieren
            filename = row.get('filename')
            if not filename or not isinstance(filename, str):
                print(f"Warnung: Zeile {index+2} hat keinen gültigen Dateinamen. Übersprungen.")
                continue
            asset_id = os.path.splitext(filename)[0].replace(' (1)', '_1').strip()
            
            # 2. Text für das Embedding erstellen
            title = row.get('llava_title', '') or ''
            desc = row.get('main_llm_description', '') or ''
            text_to_embed = f"Titel: {title}. Beschreibung: {desc}"
            
            # 3. Embedding erstellen
            embedding = model.encode(text_to_embed)

            # 4. JSON-Daten sicher bereinigen
            tags_str = clean_and_validate_json(row.get('final_asset_tags'), default_if_invalid='[]')
            platform_cats_str = clean_and_validate_json(row.get('llava_chosen_platform_leaf_categories_str'), default_if_invalid='{}')

            # 5. SQL UPSERT-Befehl
            sql_upsert = """
            INSERT INTO assets (asset_id, filename, file_format, status, llava_title, llava_description, main_llm_description, internal_category, tags, platform_categories, description_embedding, last_processed_timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            ON CONFLICT (asset_id) DO UPDATE SET
                filename = EXCLUDED.filename,
                file_format = EXCLUDED.file_format,
                status = EXCLUDED.status,
                llava_title = EXCLUDED.llava_title,
                llava_description = EXCLUDED.llava_description,
                main_llm_description = EXCLUDED.main_llm_description,
                internal_category = EXCLUDED.internal_category,
                tags = EXCLUDED.tags,
                platform_categories = EXCLUDED.platform_categories,
                description_embedding = EXCLUDED.description_embedding,
                last_processed_timestamp = NOW();
            """
            
            # 6. Befehl ausführen
            try:
                cur.execute(sql_upsert, (
                    asset_id,
                    row.get('filename'), row.get('format'), row.get('status'),
                    row.get('llava_title'), row.get('llava_description'), row.get('main_llm_description'),
                    row.get('internal_category_for_storyboard'),
                    tags_str, # Hier den bereinigten JSON-String übergeben
                    platform_cats_str, # Hier den bereinigten JSON-String übergeben
                    embedding.tolist()
                ))
                upserted_count += 1
            except Exception as e:
                print(f"!! FEHLER beim Schreiben von Asset '{asset_id}' in die DB: {e}")
                print(f"   -> Tags-Wert, der den Fehler verursachte: {tags_str}")
                print(f"   -> Platform-Cats-Wert, der den Fehler verursachte: {platform_cats_str}")
                conn.rollback() # Mache die fehlerhafte Transaktion rückgängig
                continue # Fahre mit der nächsten Zeile fort

            if (index + 1) % 10 == 0:
                print(f"  ... {index + 1}/{len(df)} Assets verarbeitet.")

    conn.commit()
    print(f"\n✅ {upserted_count} Asset(s) erfolgreich in die Datenbank geschrieben/aktualisiert.")

if __name__ == "__main__":
    print("Starte den Ingest-Prozess für Assets (Version 2)...")
    
    print("Lade Embedding-Modell...")
    embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    print("Modell geladen.")
    
    db_connection = create_connection()
    if db_connection:
        ingest_assets_from_csv(db_connection, embedding_model)
        db_connection.close()
        print("Ingest-Prozess abgeschlossen. Datenbankverbindung geschlossen.")