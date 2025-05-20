import requests
from bs4 import BeautifulSoup

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
ticker = "BITO"
datos_bito = extraer_datos_bito(ticker)

if datos_bito:
    print(f"Distribuciones de {ticker}:")
    for distribucion in datos_bito:
        print(f"  Fecha: {distribucion['fecha']}, Cantidad: {distribucion['cantidad']}")
else:
    print(f"No se encontraron distribuciones para {ticker}.")