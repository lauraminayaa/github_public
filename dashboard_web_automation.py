# Dashboard web con autenticación usando Streamlit
import streamlit as st
import pandas as pd

# Configura tu clave de acceso
CLAVE_ACCESO = 'manager2025'

st.title('Dashboard Web Privado')
clave = st.text_input('Ingresa la clave de acceso:', type='password')

if clave == CLAVE_ACCESO:
    st.success('Acceso concedido')
    # Carga tus datos (ejemplo CSV)
    archivo_csv = st.file_uploader('Selecciona tu archivo CSV', type='csv')
    if archivo_csv is not None:
        df = pd.read_csv(archivo_csv)
        st.dataframe(df)
        st.write('Estadísticas descriptivas:')
        st.write(df.describe())
        # Puedes agregar visualizaciones con st.line_chart, st.bar_chart, etc.
        st.line_chart(df)
else:
    st.warning('Acceso restringido. Ingresa la clave correcta.')
