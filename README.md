# 🎮 Proyecto de Análisis de Ventas de Videojuegos (vgsales)

## ✨ Introducción

Este proyecto tiene como objetivo principal realizar un **Análisis Exploratorio de Datos (EDA)** de ventas históricas de videojuegos. El proceso incluye la extracción, limpieza, y carga de datos desde un archivo CSV a una base de datos SQLite, seguido de una serie de análisis y visualizaciones enfocadas en tendencias de mercado, rendimiento por región y éxito de *publishers* a lo largo del tiempo.

---

## 📂 Estructura del Proyecto

La estructura de archivos refleja el flujo de trabajo completo del proyecto (ETL y Análisis):

* **`data/`**: Contiene el dataset original (`vgsales_enrique.csv`).
* **`db/`**: Almacena la base de datos SQLite (`videogames.db`) y archivos de verificación.
* **`docs/`**: Contiene soportes del proyecto.
    * **`docs/EA2/archivos/graficos/`**: 🖼️ **Directorio de Salida.** Todos los gráficos generados se guardan aquí.
* **`clean_and_load.py`**: 🐍 Script para la limpieza, transformación y carga (ETL).
* **`requirements.txt`**: Dependencias de Python.

---

## 🛠️ Flujo de Trabajo y Scripts Principales

El proyecto sigue un flujo lineal para garantizar la integridad y limpieza de los datos:

| Script | Propósito | Tarea Principal |
| :--- | :--- | :--- |
| **`clean_and_load.py`** | **Limpieza y Carga (ETL)** | Procesa el CSV, limpia los datos, y crea la tabla final `vgsales_clean` dentro de `videogames.db`. |

---

## 📈 Visualizaciones Generadas

El script de análisis cubre las siguientes áreas:

* **Tendencias de Género y Consola (hasta 2015):** Líneas de tiempo de lanzamientos y tendencias de géneros dominantes.
* **Ventas Regionales:** 5 gráficos detallando las ventas totales por género en cada región.
* **Análisis de Mercado y Publishers:**
    * Ranking de Top 10 *Publishers* por **Conteo de Juegos** y por **Ventas Totales** (hasta 2015).
    * Líneas de tiempo de **Ventas Anuales** de los Top 5 *Publishers* (hasta 2015).
* **Juegos:** Gráficos que comparan los 3 juegos más vendidos vs. los 3 menos vendidos por cada región.
* **Correlación:** **Mapa de Calor** mostrando la correlación de Pearson entre las ventas regionales y el año de lanzamiento.

---

## 📊 Fuentes y Licencias

* **Dataset:** `vgsales_enrique.csv`
    * **Fuente:** Video Game Sales
        * [https://www.kaggle.com/datasets/anandshaw2001/video-game-sales](https://www.kaggle.com/datasets/anandshaw2001/video-game-sales)
    * **Licencia:** **CC0: Public Domain** (Dominio Público)
    ### 📄 Datos en el Dataset

### 📄 Datos en el Dataset Enriquecido

El dataset contiene los siguientes atributos clave por cada videojuego (ventas medidas en **Millones** de unidades):

| Atributo | Descripción |
| :--- | :--- |
| **id** | Identificador único del registro (añadido durante la limpieza). |
| **name** | Nombre del videojuego. |
| **platform** | Plataforma o consola de lanzamiento (ej. PS2, X360, Wii). |
| **year** | Año de lanzamiento (después de la limpieza, solo incluye años válidos). |
| **genre** | Género del videojuego (ej. Action, Sports, Role-Playing). |
| **publisher** | Nombre de la compañía que publica el juego. |
| **na_sales** | Ventas en Norteamérica (North America). |
| **eu_sales** | Ventas en Europa. |
| **jp_sales** | Ventas en Japón. |
| **other_sales** | Ventas en el resto del mundo. |
| **global_sales** | Ventas totales globales (suma de las ventas regionales). |
| **release_date** | Fecha completa de lanzamiento (enriquecida). |
| **anio** | Año extraído de la fecha de lanzamiento (redundante con `year` pero útil para SQL). |
| **mes_num** | Número de mes de lanzamiento (1-12). |
| **nombre_mes** | Nombre del mes de lanzamiento. |
| **dia** | Día del mes de lanzamiento. |

## 🚀 Ejecución del Proyecto

### 1. Requisitos

Asegúrate de tener Python instalado. Instala las dependencias del proyecto ejecutando:

```bash
pip install -r requirements.txt

## 📊 Ejecución de dashboard

descargar el archivo `Vgsales_MateoLara_SimónLara.pbix` alojado en la carpeta dashboard, y abrirlo con powerBI