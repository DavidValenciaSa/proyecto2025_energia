#import pandas as pd

# Cargar el archivo CSV
#df = pd.read_csv('static/archivo/data.csv')

# Ver las primeras filas del DataFrame
#print(df.head())

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Cargar el archivo CSV

df = pd.read_csv('static/archivo/data.csv')

# Agrupar los datos por entidad (país, región, etc.) y calcular el promedio de la energía renovable
df_grouped = df.groupby('Entity')['Renewables (% equivalent primary energy)'].mean().reset_index()

# Ordenar los datos de mayor a menor para facilitar la visualización
df_grouped = df_grouped.sort_values(by='Renewables (% equivalent primary energy)', ascending=False)

# Crear el gráfico de barras
plt.figure(figsize=(10, 6))
sns.barplot(x='Renewables (% equivalent primary energy)', y='Entity', data=df_grouped, palette='viridis')

# Personalizar la gráfica
plt.title('Producción de Energía Renovable por Fuente', fontsize=14)
plt.xlabel('Porcentaje de Energía Renovable (%)')
plt.ylabel('Entidad (País, Región)')

# Mostrar el gráfico
plt.show()



