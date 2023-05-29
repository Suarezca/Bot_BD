import datetime
import os
from bs4 import BeautifulSoup

class bitacoras():
    def __init__(self):
        self.bitacora_general = []
        
    def escribir_bitacora(self, mensaje, tipo):
        fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if tipo == 'info':
            with open('Bitacoras/bitacoraInfo.log', encoding='utf-8', mode='a') as f:
                info = f'INFO/{fecha_actual}/{mensaje}\n'
                f.write(info)
                self.bitacora_general.append(info)
        elif tipo == 'error':    
            with open('Bitacoras/bitacoraError.log', encoding='utf-8', mode='a') as f:
                error = f'ERROR/{fecha_actual}/{mensaje}\n'
                f.write(error)
                self.bitacora_general.append(error)
                
    def gen_html(self):
        date_file = datetime.datetime.now().strftime('%m-%d-%Y')
        info_log_file = f"./Informes/{date_file}/Dia - {date_file}.html"

        if os.path.exists(info_log_file):    
            with open(info_log_file, encoding='utf-8', mode='r') as file:
                content = file.read()
            
            contenido = self.get_table(content)
            
        else:
            os.makedirs(f"./Informes/{date_file}", exist_ok=True)
            # Leer el archivo HTML
            with open('Resources/plantilla.html', encoding="utf-8", mode='r') as file:
                content = file.read()
            
            contenido = self.get_table(content)
        
        with open(info_log_file, encoding="utf-8", mode="w") as file:
            file.write(contenido)
        file.close()
             
    def get_table(self, content):
        # Crear un objeto BeautifulSoup para analizar el contenido HTML
        soup = BeautifulSoup(content, 'html.parser')

        # Encontrar el elemento de la tabla en el archivo HTML
        table_body = soup.find('tbody', id='table_body')

        # Agregar las filas generadas a la tabla existente
        for row in self.bitacora_general:
            lista = row.split('/')
            tipo = lista[0]
            fechaHora = lista[1]
            descripcion = lista[2]

            # Crear una nueva fila de la tabla
            new_row = soup.new_tag('tr')

            # Crear las celdas y asignarles los valores
            tipo_cell = soup.new_tag('td')
            tipo_cell.string = tipo

            fechaHora_cell = soup.new_tag('td')
            fechaHora_cell.string = fechaHora

            descripcion_cell = soup.new_tag('td')
            descripcion_cell.string = descripcion

            # Agregar las celdas a la fila
            new_row.append(tipo_cell)
            new_row.append(fechaHora_cell)
            new_row.append(descripcion_cell)

            # Agregar la fila a la tabla
            table_body.append(new_row)
        
        return str(soup.prettify())
                          
bitacora = bitacoras()