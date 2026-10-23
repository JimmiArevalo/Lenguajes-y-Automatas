"""Modelo de IA: predicción del tiempo de viaje (min) por tramo.

Datos SINTÉTICOS generados a partir de una regla física + ruido; en
producción se reemplazan por registros GPS reales de los vehículos.
Características: km, tipo de vía, hora del día, intensidad de lluvia (0-1).
"""
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split


def generar_datos(n=4000, semilla=42):
    rng = np.random.default_rng(semilla)
    km = rng.uniform(5, 35, n)
    via = rng.integers(0, 2, n)
    hora = rng.integers(4, 20, n)
    lluvia = rng.uniform(0, 1, n)
    vel = 50 - 18 * via - 14 * lluvia * (1 + via)          # km/h
    vel -= 6 * ((hora >= 6) & (hora <= 8)) + 4 * ((hora >= 16) & (hora <= 18))
    vel = np.clip(vel, 12, None)
    minutos = km / vel * 60 + rng.normal(0, 2.0, n)
    X = np.column_stack([km, via, hora, lluvia])
    return X, minutos


def entrenar(semilla=42):
    X, y = generar_datos(semilla=semilla)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=semilla)
    rf = RandomForestRegressor(n_estimators=150, random_state=semilla).fit(Xtr, ytr)
    lr = LinearRegression().fit(Xtr, ytr)
    metricas = {
        "RandomForest": (mean_absolute_error(yte, rf.predict(Xte)), r2_score(yte, rf.predict(Xte))),
        "RegresionLineal": (mean_absolute_error(yte, lr.predict(Xte)), r2_score(yte, lr.predict(Xte))),
    }
    return rf, metricas, (Xte, yte)
