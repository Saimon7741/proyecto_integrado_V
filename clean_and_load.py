import pandas as pd
import sqlite3
import os
import re
from datetime import date
import random

# --- CONFIGURACIÓN DE ARCHIVOS Y RUTAS ---
CSV_FILE = 'data/vgsales.csv'
DB_FILE = 'db/videogames.db'
TABLE_NAME = 'vgsales_clean'
EXPORT_DB_CSV_FILE = 'db/export_clean.csv'
ENRICHED_CSV_FILE = 'data/dataset_enriquecido.csv'

def setup_directories():
    """Verifica y crea los directorios necesarios."""
    os.makedirs('db', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    print("Directorios 'db' y 'data' verificados.")

def generate_random_date(year):
    """Genera una fecha aleatoria válida dentro de un año dado."""
    try:
        # Definir los límites del año
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        
        # Calcular el número de días en el año
        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days
        
        # Elegir un día aleatorio
        random_number_of_days = random.randrange(days_between_dates)
        
        # Sumar los días al 1 de enero
        random_date = start_date + pd.Timedelta(days=random_number_of_days)
        return random_date.strftime('%Y-%m-%d')
    except ValueError:
        # Manejar años inválidos (e.g., años muy antiguos o futuros si existieran)
        return None

def clean_and_enrich_data(df):
    """
    Realiza la limpieza, normalización y el enriquecimiento de datos temporales.
    """
    print("\n--- INICIO DEL PROCESO DE LIMPIEZA Y ENRIQUECIMIENTO ---")
    
    # --- FASE 1: LIMPIEZA Y NORMALIZACIÓN (Paso anterior) ---
    initial_rows = len(df)
    
    # 1. Normalizar nombres de columnas
    df.columns = [
        re.sub(r'[^a-z0-9_]', '', col.lower().replace(' ', '_')) 
        for col in df.columns
    ]
    if 'rank' in df.columns:
        df.rename(columns={'rank': 'id'}, inplace=True)
    
    # 2. Eliminar duplicados
    df.drop_duplicates(subset=['name', 'platform', 'year'], keep='first', inplace=True)
    
    # 3. Manejar valores nulos (Nulls)
    rows_before_drop = len(df)
    df.dropna(subset=['year', 'name'], inplace=True)
    df['publisher'].fillna('unknown', inplace=True)
    print(f"   - Eliminadas {rows_before_drop - len(df)} filas con nulos críticos (year o name).")

    # 4. Normalizar tipos de datos
    df['year'] = pd.to_numeric(df['year'], errors='coerce').fillna(0).astype(int) # Coerce y rellena 0s antes de int
    sale_cols = ['na_sales', 'eu_sales', 'jp_sales', 'other_sales', 'global_sales']
    for col in sale_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    for col in ['genre', 'platform', 'publisher']:
        df[col] = df[col].astype(str).str.strip().str.lower()
    
    # --- FASE 2: ENRIQUECIMIENTO TEMPORAL ---
    print("\n--- ENRIQUECIMIENTO DE DATOS TEMPORALES ---")
    
    # Verificar si el dataset tiene columna de fecha ('date' o 'release_date')
    if 'date' in df.columns or 'release_date' in df.columns:
        date_col = 'date' if 'date' in df.columns else 'release_date'
        print(f"El dataset ya contiene la columna de fecha: {date_col}. Procediendo a la derivación.")
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        
    elif 'year' in df.columns:
        print(f"El dataset solo contiene 'year'. Generando 'release_date' aleatoria dentro de cada año...")
        
        # Aplicar la generación de fecha aleatoria solo a filas con 'year' válido (> 1900)
        valid_years_df = df[df['year'] > 1900]
        
        # Crear la columna 'release_date' aplicando la función
        valid_years_df.loc[:, 'release_date'] = valid_years_df['year'].apply(generate_random_date)
        
        # Fusionar de nuevo, tratando las filas con años inválidos si las hay (aunque ya se filtraron la mayoría)
        df = valid_years_df.copy() # Usamos solo el DF con años válidos

        # Convertir a datetime para derivar componentes
        df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
        print("   - Columna 'release_date' creada.")
        
    else:
        print("ADVERTENCIA: No se encontró la columna 'year' ni ninguna columna de fecha para el enriquecimiento.")
        return df # Retorna el DF sin cambios en el tiempo
    
    # 5. CREAR NUEVAS COLUMNAS DERIVADAS
    # Los datos se extraen de la columna 'release_date' (tipo datetime)
    df['anio'] = df['release_date'].dt.year # Ya existía, pero se mantiene la consistencia
    df['mes_num'] = df['release_date'].dt.month
    df['nombre_mes'] = df['release_date'].dt.strftime('%B').str.lower()
    df['dia'] = df['release_date'].dt.day
    
    print("   - Columnas derivadas (anio, mes_num, nombre_mes, dia) añadidas con éxito.")

    # 6. GUARDAR EL DATASET ENRIQUECIDO COMO CSV
    print(f"\n6. Guardando dataset enriquecido en {ENRICHED_CSV_FILE}...")
    df.to_csv(ENRICHED_CSV_FILE, index=False)
    print(f"Dataset enriquecido guardado. Registros: {len(df)}")
    
    print("\n--- RESUMEN FINAL DE PROCESO ---")
    print(f"Registros iniciales: {initial_rows}")
    print(f"Registros finales (limpios y enriquecidos): {len(df)}")
    print(f"Nuevas columnas: ['release_date', 'mes_num', 'nombre_mes', 'dia']")
    print("--------------------------------------")
    
    return df

def load_to_sqlite(df):
    """Carga el DataFrame limpio y enriquecido a la base de datos SQLite."""
    # (El resto de la función es igual a la anterior, solo se asegura de usar el DF enriquecido)
    try:
        print(f"\n7. Conectando y cargando datos enriquecidos a SQLite en {DB_FILE}...")
        conn = sqlite3.connect(DB_FILE)
        df.to_sql(TABLE_NAME, conn, if_exists='replace', index=False)
        row_count = pd.read_sql(f'SELECT COUNT(*) FROM {TABLE_NAME}', conn).iloc[0, 0]
        print(f"¡Datos cargados con éxito! Se insertaron {row_count} registros en la tabla '{TABLE_NAME}'.")
        return conn

    except Exception as e:
        print(f"Ocurrió un error durante la carga de datos a SQLite: {e}")
        return None


def export_sqlite_to_csv(conn):
    """Exporta los datos limpios de la base de datos a un nuevo CSV de verificación."""
    # (Función de verificación sin cambios)
    try:
        print(f"\n8. Exportando datos desde SQLite a {EXPORT_DB_CSV_FILE} (Verificación)...")
        df_export = pd.read_sql(f'SELECT * FROM {TABLE_NAME}', conn)
        df_export.to_csv(EXPORT_DB_CSV_FILE, index=False)
        print(f"¡Exportación de verificación completada! Guardados {len(df_export)} registros en {EXPORT_DB_CSV_FILE}.")
        
    except sqlite3.OperationalError:
        print(f"ERROR: La tabla '{TABLE_NAME}' no existe. Asegúrate de que la carga de datos fue exitosa.")
    except Exception as e:
        print(f"Ocurrió un error durante la exportación: {e}")


if __name__ == '__main__':
    setup_directories()
    
    try:
        print(f"Cargando el archivo CSV original desde {CSV_FILE}...")
        df_raw = pd.read_csv(CSV_FILE)
        
        # Limpieza y Enriquecimiento
        df_enriched = clean_and_enrich_data(df_raw)
        
        # Cargar los datos a SQLite
        conn = load_to_sqlite(df_enriched)
        
        if conn:
            # Exportar para verificación
            export_sqlite_to_csv(conn)
            conn.close() # Cerrar la conexión
            print("\n--- PROCESO DE LIMPIEZA, ENRIQUECIMIENTO Y CARGA (ETAPA 2) FINALIZADO ---")

    except FileNotFoundError:
        print(f"\nERROR FATAL: No se encontró el archivo CSV en la ruta: {CSV_FILE}")
        print("Asegúrate de que 'vgsales.csv' esté en la carpeta 'data/'.")
    except Exception as e:
        print(f"\nOcurrió un error general en el proceso: {e}")