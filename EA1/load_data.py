import pandas as pd
import sqlite3
import os

CSV_FILE = 'data/vgsales.csv'
DB_FILE = 'db/videogames.db'
TABLE_NAME = 'vgsales'
EXPORT_CSV_FILE = 'db/verificación_datos.csv'

def setup_directories():
    """Crea los directorios 'data' y 'db' si no existen."""
    os.makedirs('db', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    print("Directorios 'db' y 'data' verificados.")

def load_csv_to_sqlite():
    """Carga los datos del CSV a una base de datos SQLite."""
    try:
        print(f"Cargando datos desde {CSV_FILE}...")
        df = pd.read_csv(CSV_FILE)

        df.columns = df.columns.str.replace('[^0-9a-zA-Z_]+', '', regex=True).str.lower()
        
        df.dropna(subset=['year'], inplace=True)
        df['year'] = df['year'].astype(int)

        print(f"Conectando a la base de datos SQLite en {DB_FILE}...")
        conn = sqlite3.connect(DB_FILE)

        df.to_sql(TABLE_NAME, conn, if_exists='replace', index=False)
        
        row_count = pd.read_sql(f'SELECT COUNT(*) FROM {TABLE_NAME}', conn).iloc[0, 0]
        print(f"¡Datos cargados con éxito! Se insertaron {row_count} registros en la tabla '{TABLE_NAME}'.")

    except FileNotFoundError:
        print(f"ERROR: No se encontró el archivo CSV en la ruta: {CSV_FILE}")
        print("Asegúrate de que 'vgsales.csv' esté en la carpeta 'data/'.")
    except Exception as e:
        print(f"Ocurrió un error durante la carga de datos: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

def export_sqlite_to_csv():
    """Exporta los datos de la base de datos a un nuevo CSV."""
    try:
        print(f"\nExportando datos desde SQLite a {EXPORT_CSV_FILE}...")
        conn = sqlite3.connect(DB_FILE)
        
        df_export = pd.read_sql(f'SELECT * FROM {TABLE_NAME}', conn)

        df_export.to_csv(EXPORT_CSV_FILE, index=False)
        
        print(f"¡Exportación completada! Se guardaron {len(df_export)} registros en {EXPORT_CSV_FILE}.")
        
    except sqlite3.OperationalError:
        print(f"ERROR: La tabla '{TABLE_NAME}' no existe o la base de datos está vacía. Ejecuta la carga primero.")
    except Exception as e:
        print(f"Ocurrió un error durante la exportación: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == '__main__':
    setup_directories()
    
    print("--- INICIO DE CARGA DE DATOS ---")
    load_csv_to_sqlite()
    
    print("\n--- INICIO DE VERIFICACIÓN ---")
    export_sqlite_to_csv()
    
    print("\n--- EXPORTACIÓN  FINALIZADA ---")