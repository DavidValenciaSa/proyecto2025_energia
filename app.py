from flask import Flask, render_template, request
import csv
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
import os
app = Flask(__name__)

# Función para leer datos del archivo CSV
def cargar_datos_renovables(ruta_csv):
    datos = []
    try:
        with open(ruta_csv, mode='r', encoding='utf-8') as archivo_csv:
            lector = csv.DictReader(archivo_csv)
            for fila in lector:
                datos.append({
                    'entity': fila['Entity'],
                    'code': fila['Code'],
                    'year': int(fila['Year']),
                    'renewables': float(fila['Renewables (% equivalent primary energy)'])
                })
    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")
    return datos

# Cargar los datos desde el archivo CSV
RUTA_CSV = 'static/archivo/data.csv'
datos_renovables = cargar_datos_renovables(RUTA_CSV)

DATA_DIR = 'static/archivo/'
    # Archivos y las columnas que queremos extraer
FILES = {
    "Wind": ("08 wind-generation.csv", "Electricity from wind (TWh)"),
    "Solar": ("12 solar-energy-consumption.csv", "Electricity from solar (TWh)"),
    "Hydropower": ("05 hydropower-consumption.csv", "Electricity from hydro (TWh)"),
    "Biofuels": ("16 biofuel-production.csv", "Biofuels Production - TWh - Total"),
    "Geothermal": ("17 installed-geothermal-capacity.csv", "Geothermal Capacity")
}
    
def load_data():
    data = {}
    for key, (file_name, column) in FILES.items():
        file_path = os.path.join(DATA_DIR, file_name)
        if os.path.exists(file_path):
            # Leer el archivo y sumar los valores de la columna correspondiente
            df = pd.read_csv(file_path)
            total_production = df[column].sum()  # Sumar la columna específica
            data[key] = total_production
    return data

@app.route('/', methods=['GET', 'POST'])
def index():
    porcentaje_renovable = None
    error = None
    
    # Cargar datos de los archivos CSV
    data = load_data()
    plt.subplots(figsize=(3, 2))
    df = pd.DataFrame(list(data.items()), columns=['Fuente', 'Producción (TWh)'])
    
    # Crear el gráfico de barras
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.bar(df['Fuente'], df['Producción (TWh)'], color=['blue', 'orange', 'green', 'red', 'purple'])

    # Configuración del gráfico
    ax.set_title('Producción de Ene. Renovable por Fuente', fontsize=14)
    ax.set_xlabel('Fuente de Energía', fontsize=12)
    ax.set_ylabel('Producción (TWh)', fontsize=12)
    
    # Convertir gráfico en imagen codificada en base64
    img = BytesIO()
    plt.tight_layout()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode('utf-8')
    
    #tortaaaaaaaaaa
    # Cargar los datos desde los archivos CSV
    df_renewables = pd.read_csv('static/archivo/04 share-electricity-renewables.csv')
    df_wind = pd.read_csv('static/archivo/11 share-electricity-wind.csv')
    df_solar = pd.read_csv('static/archivo/15 share-electricity-solar.csv')
    df_hydro = pd.read_csv('static/archivo/07 share-electricity-hydro.csv')

    # Filtrar los datos para el año más reciente (puedes ajustar esto según lo necesites)
    year = df_renewables['Year'].max()  # Año más reciente
    renewables_data = df_renewables[df_renewables['Year'] == year]
    wind_data = df_wind[df_wind['Year'] == year]
    solar_data = df_solar[df_solar['Year'] == year]
    hydro_data = df_hydro[df_hydro['Year'] == year]

    # Asumimos que los datos tienen una columna 'Entity' que es común en todos los CSV
    # Hacemos un merge de los DataFrames usando la columna 'Entity' para obtener los valores
    df = pd.merge(renewables_data[['Entity', 'Renewables (% electricity)']], 
                  wind_data[['Entity', 'Wind (% electricity)']], on='Entity')
    df = pd.merge(df, solar_data[['Entity', 'Solar (% electricity)']], on='Entity')
    df = pd.merge(df, hydro_data[['Entity', 'Hydro (% electricity)']], on='Entity')

    # Ahora, tenemos las columnas necesarias con los valores de participación para cada fuente de energía
    # Seleccionamos solo un valor para cada fuente de energía renovable
    wind_percentage = df['Wind (% electricity)'].values[0]
    solar_percentage = df['Solar (% electricity)'].values[0]
    hydro_percentage = df['Hydro (% electricity)'].values[0]

    # Asumimos que la columna de 'Renewables (%) electricity' da la suma de las energías renovables
    # Si quieres mostrarlo por separado, puedes usar la información completa de la columna
    total_renewables = wind_percentage + solar_percentage + hydro_percentage

    # Datos para el gráfico de torta
    data = {
        'Energía Renovable': ['Eólica', 'Solar', 'Hidráulica'],
        'Participación': [wind_percentage, solar_percentage, hydro_percentage]  # Porcentajes de participación
    }

    # Crear un DataFrame para el gráfico
    df_graph = pd.DataFrame(data)

    # Crear gráfico de torta
    fig, ax = plt.subplots()
    ax.set_title('Participación de Energías Renovables', fontsize=14)
    ax.pie(df_graph['Participación'], labels=df_graph['Energía Renovable'], autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Asegura que el gráfico sea un círculo.

    # Convertir el gráfico a imagen en formato base64 para poder usarlo en una web
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url2 = base64.b64encode(img.getvalue()).decode('utf-8')
    #/-----------------


    if request.method == 'POST':
        try:
            # Obtener el consumo eléctrico total del formulario
            consumo_total = float(request.form['consumo_total'])
            
            # Verificar que el consumo no sea cero o negativo
            if consumo_total <= 0:
                error = "El consumo total debe ser un valor positivo."
            else:
                # Calcular la capacidad total instalada y la producción total
                produccion_total_renovable = sum(energia['renewables'] for energia in datos_renovables)
                
                # Ajustar el cálculo del porcentaje renovable
                if produccion_total_renovable >= consumo_total:
                    porcentaje_renovable = (consumo_total / produccion_total_renovable) * 100
                else:
                    porcentaje_renovable = 100  # El consumo puede cubrirse completamente con renovables
        except ValueError:
            error = "Por favor ingrese un valor válido para el consumo total."

    return render_template('index.html', porcentaje_renovable=porcentaje_renovable, graph_url=graph_url,graph_url2=graph_url2, error=error)


if __name__ == '__main__':
    app.run(debug=True)
