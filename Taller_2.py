# -*- coding: utf-8 -*-
"""
MAESTRÍA CIENCIA DE DATOS
FUNDAMENTOS DE CIENCIA DE DATOS
UNIVERSIDAD YACHAY TECH
FECHA: 10/04/2025

@author: Magaly_Aguiar
"""
import openmeteo_requests
import requests_cache
import pandas as pd
import matplotlib.pyplot as plt
from retry_requests import retry
import os

# Crear carpeta de salida
output_folder = "C:/Users/aguia/OneDrive/MAESTRIA/FUNDAMENTOS CIENCIA DE DATOS/TALLER 2"
os.makedirs(output_folder, exist_ok=True)

# Configuración del cliente Open-Meteo con caché y reintentos
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Parámetros para la API
url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": 52.52,
    "longitude": 13.41,
    "hourly": ["temperature_2m", "rain", "uv_index"]
}
responses = openmeteo.weather_api(url, params=params)

# Procesar respuesta
response = responses[0]
print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()}{response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

# Obtener datos horarios
hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
hourly_rain = hourly.Variables(1).ValuesAsNumpy()
hourly_uv_index = hourly.Variables(2).ValuesAsNumpy()

# Crear el DataFrame
hourly_data = {
    "date": pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        closed="left"
    ),
    "temperature_2m": hourly_temperature_2m,
    "rain": hourly_rain,
    "uv_index": hourly_uv_index
}

hourly_dataframe = pd.DataFrame(data=hourly_data)


hourly_dataframe["Hora"] = hourly_dataframe["date"].dt.hour
hourly_dataframe["Fecha"] = hourly_dataframe["date"].dt.date
hourly_dataframe.drop(columns=["date"], inplace=True)
# Mostrar el DataFrame
print(hourly_dataframe)

# Graficos

# === 1. Temperatura ===
temp_por_hora = hourly_dataframe.groupby("Hora")["temperature_2m"].mean()

plt.figure(figsize=(10, 5))
plt.plot(temp_por_hora.index, temp_por_hora.values, marker='o', color='green')
plt.title("Temperatura promedio por hora (acumulado)")
plt.xlabel("Hora del día")
plt.ylabel("Temperatura promedio (°C)")
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(output_folder, "temp_promedio_por_hora.png"), dpi=300)
plt.close()

# === 2. Lluvia ===
lluvia_por_hora = hourly_dataframe.groupby("Hora")["rain"].sum()

plt.figure(figsize=(10, 5))
plt.bar(lluvia_por_hora.index, lluvia_por_hora.values, color='blue')
plt.title("Lluvia total acumulada por hora")
plt.xlabel("Hora del día")
plt.ylabel("Lluvia acumulada (mm)")
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(output_folder, "lluvia_por_hora.png"), dpi=300)
plt.close()


# === 3. Índice UV ===
uv_por_hora = hourly_dataframe.groupby("Hora")["uv_index"].mean()

plt.figure(figsize=(10, 5))
plt.plot(uv_por_hora.index, uv_por_hora.values, marker='s', color='purple')
plt.title("Índice UV promedio por hora")
plt.xlabel("Hora del día")
plt.ylabel("Índice UV")
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(output_folder, "uv_index_por_hora.png"), dpi=300)
plt.close()

#Grafico adicional con filtro de fecha 12-04-2025
df_filtrado = hourly_dataframe[hourly_dataframe["Fecha"] == pd.to_datetime("2025-04-12").date()]

plt.figure(figsize=(10, 5))
plt.plot(df_filtrado["Hora"], df_filtrado["temperature_2m"], marker='o', color='orange')
plt.title("Temperatura por hora - 14 de abril de 2025")
plt.xlabel("Hora")
plt.ylabel("Temperatura (°C)")
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(output_folder, "add_temperatura.png"), dpi=300)
plt.close()
