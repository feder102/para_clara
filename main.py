import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
from openpyxl import Workbook
import os


def get_datos(symbol):
    url = f"https://www.exchangerates.org.uk/{symbol}-exchange-rate-history.html"
    # Enviar petición GET a la página web y obtener el contenido HTML
    response = requests.get(url)
    html_content = response.content

    # Analizar el HTML con Beautiful Soup
    soup = BeautifulSoup(html_content, "html.parser")

    # Encontrar la tabla que contiene el historial de datos
    table = soup.find('table', attrs={'id':'hist'})
    datos_actuales = list()
    #Existe el archivo lo coloco en True
    lee = False
    try:
        # Abrir el archivo CSV existente y leer los datos actuales
        with open(symbol+'_exchange_rate_history.csv', mode='r') as csv_file:
            csv_reader = csv.reader(csv_file)
            datos_actuales = list(csv_reader)
            last_ele = datos_actuales[-1]
            last_ele = last_ele[0]
            last_fecha = datetime.strptime(last_ele, '%d-%m-%Y')
            datos_actuales.pop(0)
            lee = True     
    except Exception:
        last_fecha = datetime.strptime('01-01-1900', '%d-%m-%Y')
        lee = False
        pass

    borrar_archivo(symbol+'_exchange_rate_history.csv')
    with open(symbol+'_exchange_rate_history.csv', mode='w') as file:
        writer = csv.writer(file)
        try:
            rows = table.find_all('tr')
            for row in rows[2:]:
                cols = row.find_all('td')
                fecha = cols[0].text.strip()
                fecha_str = fecha
                fecha = datetime.strptime(fecha_str, "%A %d %B %Y")
                fecha_str_formato_nuevo = fecha.strftime("%d-%m-%Y")
                tipo_de_cambio = cols[1].text.strip()
                tipo_de_cambio = tipo_de_cambio.split("=")
                parte_derecha = tipo_de_cambio[1].strip() if tipo_de_cambio else ""
                tipo_de_cambio = parte_derecha.split(' ')[0]
                fila = [fecha_str_formato_nuevo, tipo_de_cambio]

                if(fecha > last_fecha):
                    datos_actuales.append(fila)                                             
            
        except Exception:
            if(datos_actuales):
                if(lee == False):
                    datos_actuales = list(reversed(datos_actuales))
                datos_actuales.insert(0,['Fecha', 'Tipo de cambio'])                       
                for dato in datos_actuales:
                    writer.writerow(dato)
            exit

def borrar_archivo(name):
    try:
        os.remove(name)
    except OSError:
        print("No se pudo borrar el archivo")
# def leer_csv(symbol):
#     try:
#         with open(symbol+'_exchange_rate_history.csv') as csv_file:
#             csv_reader = csv.reader(csv_file)
#             primera_linea = next(csv_reader)
#             primera_linea = next(csv_reader)[0]
#     except Exception:
#         primera_linea=""
#         pass
#     return primera_linea


def exportar_xlsx(symbol):
    url = f"https://www.exchangerates.org.uk/{symbol}-exchange-rate-history.html"
    # Enviar petición GET a la página web y obtener el contenido HTML
    response = requests.get(url)
    html_content = response.content

    # Analizar el HTML con Beautiful Soup
    soup = BeautifulSoup(html_content, "html.parser")

    # Encontrar la tabla que contiene el historial de datos
    table = soup.find('table', attrs={'id':'hist'})
    wb = Workbook()
    ws = wb.active
    ws.append(['Fecha', 'Tipo de cambio'])

    try:
        rows = table.find_all('tr')
        for row in rows[2:]:
            cols = row.find_all('td')
            fecha = cols[0].text.strip()
            fecha_str = fecha
            fecha = datetime.strptime(fecha_str, "%A %d %B %Y")
            fecha_str_formato_nuevo = fecha.strftime("%d-%m-%Y")
            tipo_de_cambio = cols[1].text.strip()
            tipo_de_cambio = tipo_de_cambio.split("=")
            parte_derecha = tipo_de_cambio[1].strip() if tipo_de_cambio else ""
            tipo_de_cambio = parte_derecha.split(' ')[0]
            ws.append([fecha_str_formato_nuevo, tipo_de_cambio])
    except Exception:
        pass
    wb.save(symbol + '_exchange_rate_history.xlsx')
        
if __name__ == "__main__":
    # URL a la página web
    symbols = ['ARS-CAD','USD-CAD', 'CAD-COP','COP-CAD']
    # symbols = ['ARS-CAD']
    for symbol in symbols:
       get_datos(symbol=symbol)
