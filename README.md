# 🎮 Proyecto de Análisis de Ventas de Videojuegos (vgsales)

Este proyecto tiene como objetivo extraer datos del archivo CSV de ventas de videojuegos, cargarlos en una base de datos SQLite, y demostrar la correcta ingesta y exportación de datos.

## 📊 Fuentes y Licencias

* **Dataset:** `vgsales.csv`
    * **Fuente:** Video Game Sales
        * [https://www.kaggle.com/datasets/anandshaw2001/video-game-sales](https://www.kaggle.com/datasets/anandshaw2001/video-game-sales)
    * **Licencia:** **CC0: Public Domain** (Dominio Público)

## 📁 Estructura del Proyecto

* **`data/`**: Contiene el dataset original (`vgsales.csv`).
* **`db/`**: Almacena la base de datos SQLite (`proyecto.db`) y la exportación de verificación (`export.csv`).
* **`docs/`**: (Opcional) Contiene imágenes o soportes del proyecto.
* **`load_data.py`**: Script de Python para la extracción, transformación y carga (ETL).
* **`requirements.txt`**: Dependencias de Python.

## 🚀 Ejecución del Proyecto

### 1. Requisitos

Asegúrate de tener Python instalado.

```bash
pip install -r requirements.txt
