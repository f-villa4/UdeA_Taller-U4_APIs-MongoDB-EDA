# ETL: Makeup API -> MongoDB (RAW) -> MySQL (SQL) + EDA

Proyecto educativo desarrollado para la actividad de Bases de Datos para Ciencia de Datos.
El objetivo es simular un flujo real de Ciencia de Datos usando una API publica, almacenamiento
NoSQL, transformacion con Python y analisis exploratorio.

El proyecto esta separado en tres etapas principales:

- **EXTRACT**: consume Makeup API y descarga productos reales de maquillaje.
- **TRANSFORM**: lee el raw desde MongoDB, selecciona variables relevantes y genera un CSV limpio.
- **LOAD**: carga el CSV transformado en una base de datos MySQL para consulta relacional.

Adicionalmente, incluye un notebook de **EDA** para inspeccionar los datos, calcular insights y
generar visualizaciones.

## API utilizada

La fuente de datos es **Makeup API**, una API publica con informacion de productos reales de maquillaje.

Endpoint usado:

```text
https://makeup-api.herokuapp.com/api/v1/products.json
```

Esta API retorna productos en formato JSON con campos como marca, nombre, precio, rating,
tipo de producto, categoria, etiquetas, enlaces e informacion de colores disponibles.

## Estructura del proyecto

```text
etl/
  common/
    config.py
    db.py
  extract/
    extract.py
  transform/
    transform.py
  load/
    load.py
EDA/
  analisis.ipynb
data/
  transformed/
    .gitkeep
ingesta.py
main.py
requirements.txt
.env.example
.gitignore
README.md
```

## Prerrequisitos

- Python 3.10+
- MongoDB local o una URI de MongoDB accesible
- MySQL local
- DBeaver o cualquier cliente SQL
- Jupyter Notebook
- Git

Librerias principales:

- `requests`
- `pymongo`
- `python-dotenv`
- `pandas`
- `matplotlib`
- `seaborn`
- `PyMySQL`
- `notebook`

## Preparacion rapida

Crear y activar el entorno virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instalar dependencias:

```powershell
pip install -r requirements.txt
```

Crear un archivo `.env` a partir de `.env.example`:

```powershell
copy .env.example .env
```

Editar `.env` si es necesario:

```env
MONGO_URI=mongodb://localhost:27017
MONGO_DB=taller4_db
MONGO_RAW_COLLECTION=raw_data

MAKEUP_API_URL=https://makeup-api.herokuapp.com/api/v1/products.json

TRANSFORMED_CSV_PATH=data/transformed/makeup_products.csv

DATABASE_URL=mysql+pymysql://root:tu_password@localhost:3306/makeup_etl_db
```

Es importante asegurarse de que MongoDB y MySQL esten corriendo antes de ejecutar el pipeline completo.

## Ejecucion

El archivo `ingesta.py` se incluye porque la actividad solicita explicitamente un script de ingesta.
Este script ejecuta la extraccion desde la API y guarda los datos crudos en MongoDB.

- Solo ingesta RAW a MongoDB:

  ```powershell
  python ingesta.py
  ```

- Solo extraccion usando el pipeline:

  ```powershell
  python main.py extract
  ```

- Solo transformacion (MongoDB RAW -> CSV transformado):

  ```powershell
  python main.py transform
  ```

- Solo carga (CSV transformado -> MySQL):

  ```powershell
  python main.py load
  ```

- Pipeline completo:

  ```powershell
  python main.py run
  ```

## Que hace cada etapa

### EXTRACT

- Llama al endpoint publico de Makeup API.
- Descarga la lista completa de productos disponibles.
- Valida que la respuesta de la API sea una lista de productos.
- Guarda cada producto como documento RAW en MongoDB.
- Usa el campo `id` como clave natural para evitar duplicados con `replace_one(..., upsert=True)`.

Proposito: conservar una copia fiel de la fuente original, sin limpiar ni modificar la estructura
del JSON recibido.

### RAW en MongoDB

MongoDB se usa como zona RAW porque trabaja naturalmente con documentos JSON flexibles.

Configuracion usada en la actividad:

```text
Base de datos: taller4_db
Coleccion: raw_data
```

En MongoDB, la estructura equivalente es:

```text
Base de datos -> Coleccion -> Documento -> Campo
```

Para este proyecto:

```text
taller4_db -> raw_data -> producto de maquillaje -> brand, name, price, rating, etc.
```

MongoDB agrega automaticamente el campo interno `_id`, pero el analisis excluye ese campo para
trabajar solo con la informacion de la API.

### TRANSFORM

- Lee los documentos RAW desde `taller4_db.raw_data`.
- Excluye el campo interno `_id`.
- Convierte los productos a una estructura tabular.
- Normaliza campos textuales vacios.
- Convierte `price` y `rating` a valores numericos.
- Cuenta elementos de listas como `tag_list` y `product_colors`.
- Exporta un CSV transformado en `data/transformed/makeup_products.csv`.

Columnas principales del dataset transformado:

```text
id
brand
name
product_type
category
price
rating
currency
tag_count
color_count
tags
```

Nota: cuando algunos productos no tienen categoria, se etiquetan como `uncategorized` para que
Pandas pueda analizarlos como una categoria explicita y no como un vacio invisible.

### LOAD

- Lee el CSV transformado.
- Crea la base de datos MySQL si no existe.
- Crea la tabla `makeup_products` si no existe.
- Inserta o actualiza los registros usando `INSERT ... ON DUPLICATE KEY UPDATE`.

Tabla resultante:

```text
makeup_etl_db.makeup_products
```

Proposito: practicar una salida relacional del ETL para consultar los datos con SQL y DBeaver.

## Resultados

- RAW en MongoDB: `taller4_db.raw_data`.
- Transformado en archivo: `data/transformed/makeup_products.csv`.
- SQL en MySQL: `makeup_etl_db.makeup_products`.
- Notebook de analisis: `EDA/analisis.ipynb`.

En la ejecucion local se almacenaron **931 documentos** en MongoDB, superando el minimo de
100 registros solicitado en la actividad.

Nota: los archivos CSV generados estan ignorados por `.gitignore` y no se versionan.

## Verificacion en MongoDB

Desde `mongosh`:

```javascript
use taller4_db
show collections
db.raw_data.countDocuments()
db.raw_data.findOne()
```

El conteo debe ser mayor o igual a 100.

Tambien puede verificarse desde MongoDB Compass revisando:

```text
taller4_db
  raw_data
```

## Verificacion en MySQL

Desde DBeaver o consola MySQL:

```sql
USE makeup_etl_db;

SELECT COUNT(*) FROM makeup_products;

SELECT id, brand, name, product_type, price, rating
FROM makeup_products
LIMIT 10;
```

## EDA (Jupyter Notebook)

- **Ubicacion**: carpeta `EDA/`, notebook `analisis.ipynb`.
- **Objetivo**: leer datos desde MongoDB, construir un DataFrame limpio y realizar analisis exploratorio.
- **Variables usadas**: marca, nombre, tipo de producto, categoria, precio, rating, moneda, etiquetas y colores.
- **Inspeccion basica**: primeras filas, tipos de datos, nulos y estadisticas descriptivas.
- **Visualizaciones**:
  - grafico de torta por tipo de producto;
  - grafico de barras de marcas con mas productos;
  - histograma de precios;
  - precio promedio por tipo de producto;
  - distribucion de ratings segmentados.

Para abrirlo:

```powershell
jupyter notebook EDA/analisis.ipynb
```

El notebook debe ejecutarse despues de correr la ingesta, porque lee los documentos desde MongoDB.

## Insights principales

En la ejecucion local se encontraron estos resultados:

- Total de productos analizados: 931.
- Marcas distintas: 58.
- Tipos de producto distintos: 10.
- Precio promedio de los productos: 16.51.
- Rating promedio de los productos: 4.32.
- Tipo de producto mas frecuente: `foundation`.
- Marca con mas productos registrados: `nyx`.
- Categoria mas comun: `uncategorized`.
- Promedio de colores disponibles por producto: 5.72.
- Productos sin precio: 1.5%.
- Productos sin rating: 63.5%.

El porcentaje alto de productos sin rating no invalida el analisis. Al contrario, es un hallazgo
importante sobre la calidad y completitud de los datos. Los calculos relacionados con `rating`
deben interpretarse solamente sobre los productos que si tienen ese dato disponible.

## Notas didacticas

- MongoDB se usa para conservar datos crudos en formato flexible.
- Pandas se usa para transformar documentos JSON en una tabla analitica.
- MySQL se usa como destino relacional para consultas estructuradas.
- El notebook documenta el razonamiento analitico, no solo el resultado final.
- Los valores nulos y categorias como `uncategorized` son parte normal del trabajo con APIs reales.

_Desarrollado por: Felipe Villa Velásquez_