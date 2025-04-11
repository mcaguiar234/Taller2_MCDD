# -*- coding: utf-8 -*-
"""
MAESTRÍA CIENCIA DE DATOS
FUNDAMENTOS DE CIENCIA DE DATOS
UNIVERSIDAD YACHAY TECH
FECHA: 10/04/2025

@author: Magaly_Aguiar
"""
#!pip install --user retry-requests
#from retry_requests import retry
#print("✅ Todo bien con retry_requests")
#print("✅ Todo funciona bien con requests_cache")

import openmeteo_requests
import requests_cache
import pandas as pd
import matplotlib.pyplot as plt
from retry_requests import retry
import os

output_folder = "C:/Users/aguia/OneDrive/MAESTRIA/FUNDAMENTOS CIENCIA DE DATOS/TALLER 2"
os.makedirs(output_folder, exist_ok=True)

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": 52.52,
	"longitude": 13.41,
	"hourly": ["temperature_2m", "rain", "uv_index"]
}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()}{response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
hourly_rain = hourly.Variables(1).ValuesAsNumpy()
hourly_uv_index = hourly.Variables(2).ValuesAsNumpy()

hourly_data = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
	end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	closed = "left" #Se cambia por la versión inclusive=closed
)}

hourly_data["temperature_2m"] = hourly_temperature_2m
hourly_data["rain"] = hourly_rain
hourly_data["uv_index"] = hourly_uv_index

hourly_dataframe = pd.DataFrame(data = hourly_data)
print(hourly_dataframe)

# Graficos

# === 1. Temperatura ===
plt.figure(figsize=(12, 6))
plt.plot(hourly_dataframe["date"], hourly_dataframe["temperature_2m"], label="Temperatura (°C)", color='green')
plt.xlabel("Fecha y hora")
plt.ylabel("Temperatura (°C)")
plt.title("Temperatura Horaria")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(output_folder, "temperatura.png"), dpi=300)
plt.close()

# === 2. Lluvia ===
plt.figure(figsize=(12, 6))
plt.plot(hourly_dataframe["date"], hourly_dataframe["rain"], label="Lluvia (mm)", color='blue')
plt.xlabel("Fecha y hora")
plt.ylabel("Lluvia (mm)")
plt.title("Lluvia Horaria")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(output_folder, "lluvia.png"), dpi=300)
plt.close()

# === 3. Índice UV ===
plt.figure(figsize=(12, 6))
plt.plot(hourly_dataframe["date"], hourly_dataframe["uv_index"], label="Índice UV", color='purple')
plt.xlabel("Fecha y hora")
plt.ylabel("Índice UV")
plt.title("Índice UV Horario")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(output_folder, "uv_index.png"), dpi=300)
plt.close()

