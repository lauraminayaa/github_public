# %%
# Importar librerías necesarias
import pyodbc
import os
import pandas as pd

# %%
# Conexión a SQL Server
server = 'TU_SERVIDOR'  # Ejemplo: localhost\\SQLEXPRESS
database = 'TU_BASE_DE_DATOS'
username = 'TU_USUARIO'
password = 'TU_CONTRASEÑA'
conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()
print('Conexión exitosa a SQL Server.')

# %%
# Este notebook está listo para EDA adaptable a cualquier tabla y columna de SQL Server.
# Elimina la lógica específica de arrival time y permite reutilizar el flujo para futuros proyectos.
# Solo necesitas definir el nombre de la tabla y columna que quieres analizar en las celdas siguientes.

# %%
# Puedes crear y poblar cualquier tabla según tus necesidades usando pandas y SQL Server.
# Ejemplo para insertar datos:
# df.to_sql('nombre_tabla', conn, if_exists='replace', index=False)
# Adapta este flujo para tus proyectos futuros.

# %%
# Consultar y mostrar los datos de cualquier tabla
table = 'TU_TABLA'
df_sql = pd.read_sql(f'SELECT * FROM {table}', conn)
print(df_sql)

# %% [markdown]
# # Notebook adaptable para EDA y detección de anomalías en SQL Server
# Este notebook está diseñado para automatizar consultas comunes de análisis exploratorio de datos (EDA) y detección de anomalías en cualquier tabla de SQL Server.
# Puedes reutilizarlo y adaptarlo fácilmente para futuros proyectos cambiando el nombre de la tabla y columna que deseas analizar.
# Incluye ejemplos para:
# - Estadísticas descriptivas (count, min, max, avg, stddev)
# - Identificación de nulos y duplicados
# - Búsqueda de outliers (z-score, IQR)
# - Limpieza de datos

# %%
# Automatizar consultas EDA y anomalías en cualquier tabla
def eda_sql_queries(table, column):
    queries = {
        'count': f"SELECT COUNT(*) AS total FROM {table};",
        'nulls': f"SELECT COUNT(*) AS null_count FROM {table} WHERE {column} IS NULL;",
        'duplicates': f"SELECT {column}, COUNT(*) AS dup_count FROM {table} GROUP BY {column} HAVING COUNT(*) > 1;",
        'min': f"SELECT MIN({column}) AS min_val FROM {table};",
        'max': f"SELECT MAX({column}) AS max_val FROM {table};",
        'avg': f"SELECT AVG({column}) AS avg_val FROM {table};",
        'stddev': f"SELECT STDEV({column}) AS std_val FROM {table};",
        'outliers_z': f'''SELECT *,
            (CAST({column} AS FLOAT) - (SELECT AVG(CAST({column} AS FLOAT)) FROM {table})) / NULLIF((SELECT STDEV(CAST({column} AS FLOAT)) FROM {table}),0) AS z_score
            FROM {table}
            WHERE ABS((CAST({column} AS FLOAT) - (SELECT AVG(CAST({column} AS FLOAT)) FROM {table})) / NULLIF((SELECT STDEV(CAST({column} AS FLOAT)) FROM {table}),0)) > 3;''',
    }
    return queries

# Ejemplo de uso:
table = 'TU_TABLA'
column = 'TU_COLUMNA'
queries = eda_sql_queries(table, column)
for name, q in queries.items():
    print(f'--- {name.upper()} ---')
    try:
        df = pd.read_sql(q, conn)
        print(df)
    except Exception as e:
        print('Error:', e)

# %%
# Visualización de resultados y anomalías con Plotly
import plotly.express as px
# Ejemplo: visualiza la columna numérica y resalta outliers (z-score > 3)
column = 'TU_COLUMNA'
df_sql['z_score'] = (df_sql[column] - df_sql[column].mean()) / df_sql[column].std()
fig = px.scatter(df_sql, x=df_sql.index, y=column, color=df_sql['z_score'].abs() > 3,
                  title=f'Visualización de {column} y outliers (z-score > 3)', labels={'color': 'Outlier'})
fig.show()

# %%
# Limpieza de datos: eliminar nulos y duplicados
# Eliminar filas con nulos en la columna seleccionada
column = 'TU_COLUMNA'
cursor.execute(f"DELETE FROM {table} WHERE {column} IS NULL;")
conn.commit()
print(f'Se eliminaron filas con nulos en {column}.')
# Eliminar duplicados (mantener el primero)
# NOTA: SQL Server no tiene DELETE ... USING, así que se recomienda hacerlo con una CTE
cursor.execute(f'''WITH CTE AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY {column} ORDER BY (SELECT 0)) AS rn
    FROM {table} )
DELETE FROM CTE WHERE rn > 1;''')
conn.commit()
print(f'Se eliminaron duplicados en {column}.')

# %%
# (Opcional) Reporte interactivo de EDA con ydata-profiling
try:
    from ydata_profiling import ProfileReport
    profile = ProfileReport(df_sql, title='Reporte EDA ydata-profiling', explorative=True)
    profile.to_notebook_iframe()
except ImportError:
    print('ydata-profiling no está instalado. Ejecuta "pip install ydata-profiling" para usar esta función.')


