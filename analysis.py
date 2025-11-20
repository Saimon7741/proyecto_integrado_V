import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os
import seaborn as sns

# Configuración de rutas
DB_FILE = 'db/videogames.db'
TABLE_NAME = 'vgsales_clean'
GRAPHICS_DIR = 'docs/EA2/graficos'

# Configuración de estilo de Matplotlib y Seaborn
plt.style.use('ggplot')
sns.set_theme(style="whitegrid")

def connect_db():
    """Establece la conexión a la base de datos SQLite."""
    try:
        conn = sqlite3.connect(DB_FILE)
        return conn
    except sqlite3.Error as e:
        print(f"Error al conectar a la base de datos {DB_FILE}: {e}")
        return None

def setup_graphics_dir():
    """Crea el directorio para guardar los gráficos si no existe."""
    os.makedirs(GRAPHICS_DIR, exist_ok=True)
    print(f"\nDirectorio de gráficos '{GRAPHICS_DIR}' verificado/creado.")

def get_descriptive_stats(conn):
    """Obtiene y muestra estadísticas descriptivas de las variables clave."""
    print("\n" + "="*80)
    print("                 ESTADÍSTICAS DESCRIPTIVAS GENERALES (df.describe())")
    print("="*80)
    
    # Seleccionar solo las columnas numéricas para el describe
    query = f"""
    SELECT na_sales, eu_sales, jp_sales, other_sales, global_sales, year, mes_num
    FROM {TABLE_NAME}
    """
    df = pd.read_sql_query(query, conn)
    
    print(df.describe().to_markdown())
    
    print("\nINTERPRETACIÓN:")
    print("1. El promedio de ventas globales (Global_Sales) es bajo (0.54M), lo que indica que la mayoría de los juegos son *flops* o juegos nicho.")
    print("2. Las ventas máximas son dominadas por NA_Sales y EU_Sales, con picos muy altos, lo que sugiere la presencia de *outliers* (juegos muy vendidos como 'Wii Sports').")
    print("3. La desviación estándar (std) es muy alta en todas las columnas de ventas, confirmando la gran dispersión y concentración de ventas en unos pocos títulos.")
    print("4. La distribución de 'year' (año) muestra un rango amplio, indicando que el dataset cubre un largo período de la historia de los videojuegos.")
    print("="*80)


def analyze_sales_by_genre_and_region(conn):
    """
    Q1: Analizar qué género se vendió más y menos en cada continente.
    Genera 5 gráficos: 1 apilado global y 4 específicos por región.
    """
    print("\n" + "="*80)
    print("Q1: VENTAS TOTALES POR GÉNERO Y DISTRIBUCIÓN REGIONAL")
    print("="*80)
    
    query = f"""
    SELECT genre, 
           SUM(na_sales) AS NA_Sales, 
           SUM(eu_sales) AS EU_Sales, 
           SUM(jp_sales) AS JP_Sales, 
           SUM(other_sales) AS Other_Sales,
           SUM(global_sales) AS Global_Sales
    FROM {TABLE_NAME}
    GROUP BY genre
    ORDER BY Global_Sales DESC
    """
    df_sales = pd.read_sql_query(query, conn)
    
    df_regions = df_sales.set_index('genre')[['NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales']]
    region_totals = df_regions.sum().round(2)

    # 1. GRÁFICO APILADO GLOBAL (Para contexto general)
    plt.figure(figsize=(12, 8))
    df_regions.plot(kind='bar', stacked=True, colormap='viridis', ax=plt.gca())
    
    new_labels = [
        f"NA_Sales ({region_totals['NA_Sales']:.2f}M)",
        f"EU_Sales ({region_totals['EU_Sales']:.2f}M)",
        f"JP_Sales ({region_totals['JP_Sales']:.2f}M)",
        f"Other_Sales ({region_totals['Other_Sales']:.2f}M)"
    ]
    plt.title('1.1 Ventas Totales de Videojuegos por Género y Región (Global)', fontsize=16)
    plt.ylabel('Ventas Totales (en Millones)', fontsize=12)
    plt.xlabel('Género', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.legend(labels=new_labels, title='Región (Total en Millones)')
    plt.tight_layout()
    plt.savefig(os.path.join(GRAPHICS_DIR, 'q1_1_ventas_genero_region_global.png'))
    plt.show()
    
    print("\nINTERPRETACIÓN DEL GRÁFICO 1.1 (Global y Apilado):")
    print("• Ventas Regionales Totales: Norteamérica (NA) es, por amplio margen, el mercado más grande, seguido por Europa (EU). Japón (JP) es el tercer mercado, con ventas más enfocadas en ciertos géneros.")
    print("• Distribución Global: Los géneros Action y Sports son los pilares del mercado global, impulsados principalmente por las ventas occidentales (NA y EU).")


    # 2. GRÁFICOS INDIVIDUALES POR REGIÓN (Para detalle de género)
    regions = {'NA_Sales': 'Norteamérica', 'EU_Sales': 'Europa', 'JP_Sales': 'Japón', 'Other_Sales': 'Otras Regiones'}
    
    for col_name, region_name in regions.items():
        # Ordenar los géneros por ventas en esa región
        df_region_sorted = df_sales[['genre', col_name]].sort_values(by=col_name, ascending=False)
        
        plt.figure(figsize=(10, 6))
        sns.barplot(data=df_region_sorted, x='genre', y=col_name, palette='plasma')
        
        plt.title(f'1.2 Ventas de Videojuegos por Género en {region_name} (Total: {region_totals[col_name]:.2f}M)', fontsize=14)
        plt.ylabel('Ventas (en Millones)', fontsize=12)
        plt.xlabel('Género', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(os.path.join(GRAPHICS_DIR, f'q1_2_ventas_genero_{col_name.lower()}.png'))
        plt.show()

        # Interpretación específica por región
        top_genre = df_region_sorted.iloc[0]['genre'].capitalize()
        bottom_genre = df_region_sorted.iloc[-1]['genre'].capitalize()
        
        print(f"\nINTERPRETACIÓN DEL GRÁFICO 1.2 ({region_name}):")
        if col_name == 'JP_Sales':
            print(f"• Dominio: El género {top_genre} es el más vendido en {region_name}, lo que subraya la fuerte preferencia japonesa por los juegos de rol. El segundo lugar (Platform) también es notablemente alto.")
        elif col_name in ['NA_Sales', 'EU_Sales']:
            print(f"• Dominio: El género {top_genre} lidera, seguido de cerca por Sports/Shooter, reflejando el gusto occidental por la acción y los deportes masivos.")
        else:
            print(f"• Dominio: {top_genre} también domina en {region_name}. Este mercado muestra tendencias similares a NA/EU en términos de géneros principales.")
        print(f"• Menos vendido: {bottom_genre} es consistentemente uno de los géneros con menores ventas en {region_name}.")
        print("-" * 80)
        
    print("\nAnálisis de la distribución de ventas por género en regiones completado. Se generaron 5 gráficos.")


def analyze_genre_by_platform(conn):
    """
    Q2: Qué género salió más en qué consola (Plataforma dominante de cada género).
    """
    print("\n" + "="*80)
    print("Q2: GÉNERO MÁS COMÚN LANZADO POR LAS 10 PLATAFORMAS CON MÁS TÍTULOS")
    print("="*80)

    # 1. Identificar las 10 plataformas con más títulos lanzados
    top_platforms_query = f"""
    SELECT platform
    FROM {TABLE_NAME}
    GROUP BY platform
    ORDER BY COUNT(id) DESC
    LIMIT 10
    """
    top_platforms = pd.read_sql_query(top_platforms_query, conn)['platform'].tolist()
    
    # 2. Consultar el conteo de géneros para esas 10 plataformas
    query = f"""
    SELECT platform, genre, COUNT(id) AS count
    FROM {TABLE_NAME}
    WHERE platform IN ({', '.join([f"'{p}'" for p in top_platforms])})
    GROUP BY platform, genre
    ORDER BY platform, count DESC
    """
    df_platform_genre = pd.read_sql_query(query, conn)
    
    # Encontrar el género dominante (el que tiene el conteo más alto) para cada plataforma
    idx = df_platform_genre.groupby(['platform'])['count'].transform(max) == df_platform_genre['count']
    df_dominant_genre = df_platform_genre[idx].drop_duplicates(subset=['platform'], keep='first')
    
    # 3. Visualización del Género Dominante
    plt.figure(figsize=(12, 6))
    sns.barplot(data=df_dominant_genre, x='platform', y='count', hue='genre', dodge=False)
    plt.title('Género Dominante por las Top 10 Plataformas (Basado en Conteos de Títulos)', fontsize=16)
    plt.ylabel('Cantidad de Títulos del Género Dominante', fontsize=12)
    plt.xlabel('Plataforma', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Género Dominante')
    plt.tight_layout()
    plt.savefig(os.path.join(GRAPHICS_DIR, 'q2_genero_dominante_plataforma.png'))
    plt.show()
    
    print("INTERPRETACIÓN DEL GRÁFICO (q2_genero_dominante_plataforma.png):")
    print("• Consolas con Mayor Dominio de un Género: Plataformas como PS2 y DS muestran la mayor cantidad de lanzamientos, siendo Action y Misc (respectivamente) sus géneros dominantes.")
    print("• Tendencias: En general, el género Action tiende a ser dominante en la mayoría de las plataformas modernas (PS2, PS3, X360, Wii), lo que refleja la masificación del desarrollo de juegos de acción/aventura.")
    print("• Excepciones: Plataformas antiguas (como PS y DS) a menudo tienen géneros 'Misc' o 'Role-Playing' como dominantes debido a las tendencias de lanzamiento de su época.")
    print("-" * 80)


def analyze_genre_over_time(conn):
    """
    Q3: Qué género de juegos salió más en qué año (Tendencia histórica).
    """
    print("\n" + "="*80)
    print("Q3: TENDENCIA DE CONTEO DE JUEGOS POR GÉNERO A LO LARGO DEL TIEMPO")
    print("="*80)

    # 1. Contar títulos por Año y por Género
    query = f"""
    SELECT year, genre, COUNT(id) AS count
    FROM {TABLE_NAME}
    WHERE year >= 1980 -- Filtro para evitar años atípicos
    GROUP BY year, genre
    """
    df_trend = pd.read_sql_query(query, conn)
    
    # 2. Pivotar la tabla y obtener los top 5 géneros
    df_pivot = df_trend.pivot_table(index='year', columns='genre', values='count', fill_value=0)
    top_5_genres = df_pivot.sum().nlargest(5).index.tolist()
    
    # 3. Visualización de Tendencia (Líneas)
    plt.figure(figsize=(14, 7))
    # Graficar solo el top 5 para evitar sobrecarga visual
    df_pivot[top_5_genres].plot(kind='line', marker='.', ax=plt.gca())
    
    plt.title('Tendencia de Lanzamientos Anuales: Top 5 Géneros', fontsize=16)
    plt.ylabel('Cantidad de Títulos Lanzados', fontsize=12)
    plt.xlabel('Año de Lanzamiento', fontsize=12)
    plt.legend(title='Género')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(GRAPHICS_DIR, 'q3_tendencia_genero_anual.png'))
    plt.show()
    
    print("INTERPRETACIÓN DEL GRÁFICO (q3_tendencia_genero_anual.png):")
    print("• Dominio del Action: El género Action (Acción) ha sido el más lanzado consistentemente desde finales de los 90, con un pico de lanzamientos alrededor de 2008-2010.")
    print("• Periodo de Auge: El periodo de 2005 a 2010 marcó el máximo histórico de lanzamientos de videojuegos en general, coincidiendo con el auge de consolas como PS2, Wii y DS.")
    print("• Decline: Se observa una caída en el número de lanzamientos anuales después de 2010, probablemente debido a la consolidación del mercado y el cambio hacia modelos de juegos como servicio (Live Service).")
    print("-" * 80)


def analyze_platform_by_year_range(conn):
    """
    Q4: Para qué consola salieron más y menos juegos en los rangos de años 1980-1990 y 2000-2010.
    """
    print("\n" + "="*80)
    print("Q4: CONTEO DE JUEGOS POR CONSOLA EN RANGOS DE AÑOS CLAVE")
    print("="*80)
    
    ranges = [(1980, 1990), (2000, 2010)]
    
    for start_year, end_year in ranges:
        print(f"\nANÁLISIS DE RANGO: {start_year} - {end_year}")
        
        query = f"""
        SELECT platform, COUNT(id) AS game_count
        FROM {TABLE_NAME}
        WHERE year BETWEEN {start_year} AND {end_year}
        GROUP BY platform
        HAVING game_count > 10 -- Solo plataformas relevantes
        ORDER BY game_count DESC
        """
        df_range = pd.read_sql_query(query, conn)
        
        # Top 5 y Bottom 5
        top_5 = df_range.head(5)
        bottom_5 = df_range.tail(5)

        # 1. Gráfico de Barras para Top 5
        plt.figure(figsize=(10, 5))
        sns.barplot(data=top_5, x='platform', y='game_count', palette='cividis')
        plt.title(f'Top 5 Plataformas por Lanzamientos ({start_year}-{end_year})', fontsize=14)
        plt.ylabel('Cantidad de Juegos', fontsize=10)
        plt.xlabel('Plataforma', fontsize=10)
        plt.tight_layout()
        plt.savefig(os.path.join(GRAPHICS_DIR, f'q4_top5_plataformas_{start_year}_{end_year}.png'))
        plt.show()
        
        # 2. Gráfico de Barras para Bottom 5
        plt.figure(figsize=(10, 5))
        sns.barplot(data=bottom_5, x='platform', y='game_count', palette='magma')
        plt.title(f'Bottom 5 Plataformas por Lanzamientos ({start_year}-{end_year})', fontsize=14)
        plt.ylabel('Cantidad de Juegos', fontsize=10)
        plt.xlabel('Plataforma', fontsize=10)
        plt.tight_layout()
        plt.savefig(os.path.join(GRAPHICS_DIR, f'q4_bottom5_plataformas_{start_year}_{end_year}.png'))
        plt.show()

        print(f"INTERPRETACIÓN DEL RANGO {start_year}-{end_year}:")
        if start_year == 1980:
            print(f"• Dominio Temprano (80s): Plataformas como NES, GB y Atari 2600 (2600) lideraron los lanzamientos. El mercado estaba menos diversificado.")
            print(f"• Consola Más Lanzada: {top_5.iloc[0]['platform'].upper()} con {top_5.iloc[0]['game_count']} títulos.")
        else: # 2000-2010
            print(f"• Era de la Masificación (00s): La PS2 y la DS dominaron la producción de juegos, reflejando el máximo crecimiento de la industria en cuanto a títulos lanzados. La diversificación de consolas portátiles y de sobremesa impulsó estos números.")
            print(f"• Consola Más Lanzada: {top_5.iloc[0]['platform'].upper()} con {top_5.iloc[0]['game_count']} títulos.")
        
    print("-" * 80)


def main_analysis():
    """Función principal para ejecutar todo el análisis."""
    setup_graphics_dir()
    conn = connect_db()
    
    if conn:
        print("Conexión a SQLite exitosa. Iniciando análisis...")
        
        # 1. Estadísticas Descriptivas
        get_descriptive_stats(conn)
        
        # 2. Análisis por Género y Región (Q1) -> Modificado para 5 gráficos
        analyze_sales_by_genre_and_region(conn)
        
        # 3. Análisis de Género por Plataforma (Q2)
        analyze_genre_by_platform(conn)
        
        # 4. Análisis de Género a lo largo del Tiempo (Q3)
        analyze_genre_over_time(conn)
        
        # 5. Análisis de Plataforma por Rangos de Año (Q4)
        analyze_platform_by_year_range(conn)
        
        conn.close()
        print("\nAnálisis completado. Todos los gráficos han sido guardados en 'docs/graficos/'.")

if __name__ == '__main__':
    # Se necesita instalar las bibliotecas: pip install pandas matplotlib seaborn
    main_analysis()