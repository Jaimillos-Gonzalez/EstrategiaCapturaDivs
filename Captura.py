import requests
from bs4 import BeautifulSoup
import time
import yfinance as yf
import pandas as pd

#USANDO LA LIBRERIA DE YAHOO
def getDataFromYahooUsingAPI(tickerAnalisis):
    ticker = yf.Ticker(tickerAnalisis)
    hist = ticker.history(period="1y")
    hist = hist.reset_index()

    hist_selected = hist[['Date','Open', 'Close', 'Dividends']]
    hist_selected = hist_selected.reset_index()


    # Filtrar solo filas con dividendos
    div_rows = hist[hist["Dividends"] > 0].copy()
    # Crear lista para resultados
    resultados = []

    # Recorrer filas con dividendos
    for _, row in div_rows.iterrows():
        fecha_exdate = row['Date']
        dividendo = row['Dividends']

        # Buscar fila del día anterior
        idx = hist[hist['Date'] < fecha_exdate].last_valid_index()
        if idx is None:
            continue
        fila_anterior = hist.loc[idx]

        # Extraer valores
        precio_cierre_dia_anterior = round(fila_anterior['Close'], 2)
        precio_apertura_exdate = round(row['Open'], 2)

        # Cálculos
        porcentaje_dividendo = dividendo / precio_cierre_dia_anterior
        variacion_precio = -((precio_cierre_dia_anterior - precio_apertura_exdate) / precio_cierre_dia_anterior)
        rentabilidad_total = porcentaje_dividendo + variacion_precio

        # Agregar fila de resultados
        resultados.append({
            "Fecha": fecha_exdate.date(),
            "Precio Cierre día ExDate -1": round(precio_cierre_dia_anterior, 2),
            "Precio Apertura día ExDate": round(precio_apertura_exdate, 2),
            "Dividendo": round(dividendo, 4),
            "% Dividendo": round(porcentaje_dividendo * 100, 2),
            "% Variacion Precio": round(variacion_precio * 100, 2),
            "Rentabilidad Op.": round(rentabilidad_total * 100, 2)
        })

    # Convertir a DataFrame
    df_resultados = pd.DataFrame(resultados)

    df_resultados.to_excel(f"{tickerAnalisis}_precios.xlsx", index=False)




def extraer_datos_bito(ticker):
    """
    Extrae datos de "dividendos" (distribuciones) de la página de historial de Yahoo Finance para un ticker dado.

    Args:
        ticker: El símbolo ticker del ETF (por ejemplo, "BITO").

    Returns:
        Una lista de diccionarios, donde cada diccionario contiene la fecha y la cantidad del "dividendo" (distribución).
    """

    url = f"https://finance.yahoo.com/quote/{ticker}/history"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lanza una excepción para códigos de estado HTTP erróneos
        time.sleep(5)

        soup = BeautifulSoup(response.content, 'html.parser')

        # Encuentra la tabla de historial
        tabla = soup.find('table', {'class': 'W(100%) M(0)'})

        if tabla is None:
            print("No se encontró la tabla de historial en la página.")
            return []

        # Extrae las filas de la tabla
        filas = tabla.find_all('tr')

        datos = []
        for fila in filas[1:]:  # Ignora la fila de encabezado
            celdas = fila.find_all('td')
            if len(celdas) > 1:
                fecha = celdas[0].text
                evento = celdas[1].text

                if "Dividend" in evento:
                    cantidad = float(evento.split(" ")[0])  # Extrae la cantidad antes de "Dividend"
                    datos.append({'fecha': fecha, 'cantidad': cantidad})

        return datos

    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")
        return []
    except Exception as e:
        print(f"Error inesperado: {e}")
        return []

# Ejemplo de uso:
getDataFromYahooUsingAPI("BITO")


ticker = "BITO"
datos_bito = extraer_datos_bito(ticker)

if datos_bito:
    print(f"Distribuciones de {ticker}:")
    for distribucion in datos_bito:
        print(f"  Fecha: {distribucion['fecha']}, Cantidad: {distribucion['cantidad']}")
else:
    print(f"No se encontraron distribuciones para {ticker}.")