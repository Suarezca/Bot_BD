from selenium import webdriver
from selenium.webdriver.common.by import By
from tkinter import messagebox
from enviar_email import enviar_correo
import time
import keyboard
import configparser
import requests
import re
import logging
import datetime
from selenium.common.exceptions import WebDriverException
import os
from bs4 import BeautifulSoup
from Logg import logg_actions, logg_errors
from datetime import datetime


class Principal(object):

    def cred_bd():
        try:
            #template = env.get_template('informe.html')
            # Pide el nombre del archivo que contiene las credenciales de la base de datos
            nombre_archivo = "Configuraciones/credenciales_bd.txt"

            # Lee las credenciales de la base de datos desde el archivo especificado
            with open(nombre_archivo, "r") as f:
                lines = f.readlines()

            # Crea un diccionario a partir de las líneas del archivo
            credenciales = {}
            for line in lines:
                # Verifica que la línea contenga el carácter ":"
                if " " not in line:
                    continue
                key, value = line.strip().split(" ")
                credenciales[key] = value.strip()

            # Configura las opciones del navegador
            # 
            options = webdriver.ChromeOptions()
            options.add_experimental_option("detach", True)

            # Crea una instancia del navegador
            # driver = webdriver.Chrome(options=options)
            driver = webdriver.Chrome()
            driver.implicitly_wait(10)

            try:
                driver.get(credenciales['host'])
            except WebDriverException:
                print("Error: Host mal escrito")
        
                time.sleep(2)
                driver.close()

            # Ingresa las credenciales de inicio de sesión
            user = credenciales['user']
            password = credenciales['password']
            username_field = driver.find_element(By.NAME, value= 'user')
            username_field.send_keys(user)

            password_field = driver.find_element(By.NAME, value='pass')
            password_field.send_keys(password)
        except Exception as error:
            messagebox.showerror(title="Host Error", message="El HOST de la BD no es el correcto.")
            enviar_correo(contenido="Surgio una excepcion de tipo: ",error="Verifica HOST",asunto="Bot system error")
            logger_comun.error("Verifique que el HOST este correctamente escrito.")
        
        #---------------------------CLICK INICIAR SECION---------------------------------
        try:

            search_box = driver.find_element(by=By.ID, value='login_submit')
            search_box.click()
            time.sleep(2)
        except Exception as error:
            messagebox.showerror(title="Click Iniciar Sesion", message="Hubo un error al intentar presionar click.")
            enviar_correo(contenido="Surgio una excepcion de tipo: ",error=error,asunto="Bot system error")
            exit()
            # driver.close()

        #----------------------ABRE LA BD-----------------------------------------------
        try:
            current_url = driver.current_url

            dominio = str(current_url).split('/phpMyAdmin/')[0]
            

            ruta_all = f'{dominio}/phpMyAdmin/index.php?route=/database/structure&db={credenciales["bd_name"]}'
            # print(ruta_all)
            driver.get(ruta_all)
            time.sleep(1)
        except Exception as error:
            messagebox.showerror(title="Abrir base datos", message="No es posible abrir la BD, revise los parametros")
            enviar_correo(contenido="Surgio una excepcion de tipo: ",error=error,asunto="Bot system error")
            # driver.close()

        #---------------------------CLICK SQL---------------------------------
        try:
            click_sql = driver.find_element(by=By.XPATH, value='/html/body/div[5]/div/nav/div/ul/li[2]/a')
            click_sql.click()
        except Exception as error:
            messagebox.showerror(title="Datos incorrectos", message="Verifique si el usuario o la contraseña sean correctos")
            enviar_correo(contenido="Surgio una excepcion de tipo: ",error="Usuario o contraseña incorrecta",asunto="Bot system error")
            logger_comun.error("Usuario o contrasen va invalidos.")
            exit()
            # driver.close()

        #---------------------------CLICK LIMPIAR---------------------------------
        try:
            clear = driver.find_element(by=By.ID, value='clear')
            clear.click()
            # time.sleep(2)
        except Exception as error:
            messagebox.showerror(title="Nombre incorrecto", message="No es posible continuar, rectifique su nombre de BD")
            enviar_correo(contenido="Surgio una excepcion de tipo: ",error="Nombre de BD mal escrita, revise archivo de credenciales",asunto="Bot system error")
            logger_comun.error("Alguien ha ingresado mal el nombre de la BD.")
            # driver.close()
            
        #-------------------------ARCHIVO RUTINAS--------------------------------
        try: 
            ruta_archivo = "Configuraciones/rutinas.txt"

            # Lee las líneas del archivo de configuración y las guarda en una lista
            with open(ruta_archivo, "r") as archivo:
                lineas = archivo.readlines()


            sql = ''.join(lineas)

            caracteres = {
                ' ':'space',
                '\n':'enter',
                ';':'shift+;',
                '(':'shift+8',
                ')':'shift+9',
                '[':'shift+{',
                ']':'shift+}',
                '_':'shift+_',
                '=':'shift+0'
            }
        except Exception as error:
            messagebox.showerror(tittle="Archivo rutinas", message="No fue posible leer el archivo")
            enviar_correo(contenido="Surgio una excepcion de tipo: ",error=error,asunto="Bot system error")
        try:
            for char in sql:
                keyboard.press_and_release(caracteres.get(char.lower(), char.lower()))
                time.sleep(.2)
                
            time.sleep(1)

            save = driver.find_element(by=By.XPATH, value='/html/body/div[7]/form/div/div[3]/div/div[6]/input')

            # Hacer scroll hasta el elemento
            driver.execute_script("arguments[0].scrollIntoView();", save)
            time.sleep(1)
            save.click()
            
            
        except Exception as error:
            messagebox.showerror(title="Cambios en BD", message="No fue posible guardar los cambios")
            enviar_correo(contenido="Surgio una excepcion de tipo: ",error=error,asunto="Bot system error")
            # driver.close()

#------------------------------------------------------------------------------------------------------                
    # try:
        # Busca los elementos que tienen la clase "sql-highlight cm-s-default"
        elementos = driver.find_elements(by=By.CSS_SELECTOR, value=".sql-highlight.cm-s-default")

        # Obtiene la fecha y hora actual
        fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if elementos:
            # Se encontraron elementos con la clase "sql-highlight cm-s-default", se considera una consulta buena
            # Abre el archivo de bitácora de consultas buenas en modo de escritura
            
            logg_actions("ERROR DE EJECUCION --- Prueba")
            with open('bitacoraInfo.log', 'a') as file:
                for elemento in elementos:
                    # Captura el texto de cada elemento
                    texto = elemento.text

                    # Formatea el mensaje de consulta buena con el nivel de registro y la fecha y hora
                    mensaje_consulta = f"COMPLETO/{fecha_actual}/{texto}"

                    # Escribe el mensaje de consulta buena en la bitácora de consultas buenas
                    file.write(mensaje_consulta + "\n")
        else:
            
            # Intenta capturar el texto de los elementos XPath originales
            alerta = None
            alerta2 = None
            elementos_xpath = driver.find_elements(by=By.XPATH, value='//*[@id="sqlqueryresultsouter"]/div/pre/code')
            logg_errors(elementos_xpath)
            if elementos_xpath:
                alerta = elementos_xpath[0].text
            elementos_xpath2 = driver.find_elements(by=By.XPATH, value='//*[@id="sqlqueryresultsouter"]/div/code')
            if elementos_xpath2:
                alerta2 = elementos_xpath2[0].text

            if alerta is not None and alerta2 is not None:
                texto_completo = alerta + " " + alerta2

                with open('bitacoraInfo.log', 'a') as file:
                    for linea in lineas:
                        linea = linea[:-1] if linea[-1]=='\n' else linea
                        linea = linea if linea[-1]==';' else linea+';'
                        
                        if linea.upper() == alerta.upper():
                            break
                            
                        mensaje_correcto = f"COMPLETADO/{fecha_actual}/{linea}"
                        file.write(mensaje_correcto + "\n")
                    
                # if not existe_error:
                    # Abre el archivo de bitácora de errores en modo de escritura
                with open('bitacoraError.log', 'a') as file:
                    # Formatea el mensaje de error con el nivel de registro y la fecha y hora
                    mensaje_error = f"ERROR/{fecha_actual}/{texto_completo}"

                    # Escribe el mensaje de error en la bitácora de errores
                    file.write(mensaje_error + "\n")
        global rutina
        rutina = sql
# #---------------------------------------------------------------------------------------------------------------------------------        
    def generar_html():
        date_file = datetime.now().strftime('%m-%d-%Y')
        
        # Obtener el contenido de la bitácora de consultas buenas del archivo
        info_log_file = f"./Logg/{date_file}/Actions - {date_file}.log", "a"
        with open(info_log_file) as file:
            info_log_data = file.read()
        
        # Obtener el contenido de la bitácora de errores del archivo
        error_log_file = f"./Logg/{date_file}/Actions - {date_file}.log", "a"
        with open(error_log_file, 'r') as file:
            error_log_data = file.read()

        # Crear una función para generar las filas de la tabla
        def generate_table_rows(log_data):
            table_rows = []
            lines = log_data.split('\n')

            for line in lines:
                if line.strip() != '':
                    fields = line.split('---')
                    tipo = fields[0]
                    fechaHora = fields[1]
                    descripcion = fields[2]

                    # Crear una nueva fila de la tabla
                    new_row = [tipo, fechaHora, descripcion]
                    # Agregar la fila a la lista
                    table_rows.append(new_row)
            return table_rows

        # Generar las filas de la tabla para la bitácora de consultas buenas
        info_table_rows = generate_table_rows(info_log_data)
        
        # Generar las filas de la tabla para la bitácora de errores
        error_table_rows = generate_table_rows(error_log_data)

        # Leer el archivo HTML
        with open('plantilla.html', 'r') as file:
            content = file.read()

        # Crear un objeto BeautifulSoup para analizar el contenido HTML
        soup = BeautifulSoup(content, 'html.parser')

        # Encontrar el elemento de la tabla en el archivo HTML
        table_body = soup.find('tbody', id='table_body')

        # Agregar las filas generadas a la tabla existente
        for row in info_table_rows + error_table_rows:
            tipo = row[0]
            fechaHora = row[1]
            descripcion = row[2]

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

        # Guardar los cambios en el archivo HTML
        with open('informe.html', 'w') as file:
            file.write(str(soup.prettify()))
            
# #---------------------------------------------------------------------------------------------------------------------------      
      
# #------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    
    try: 
        url = "http://henry-sanchez.com/gbm/verificationcode/codes.txt"
        config = configparser.ConfigParser()
        response = requests.get(url)
        contenido = response.text
        
        
        logging.basicConfig(filename='bitacoraError.log', level=logging.ERROR,
                            format="""%(levelname)s/%(asctime)s/%(message)s""")
        
        logger_comun = logging.getLogger()
        
        
        try:
            codigo_verificacion = re.findall(r".*(?:\w*?|\d*?|\$*?|\#*?|\&*?|\%*?|\-*?)\S", contenido)
            
            codigo_usuario = input("Ingrese codigo de verificación: -- ")
            if codigo_usuario in codigo_verificacion:
                
                
                logging.basicConfig(filename='bitacoraInfo.log', level=logging.INFO,
                            format="""%(levelname)s/%(asctime)s/%(message)s""")
                logger_exit = logging.getLogger()
                
                
                #Principal.cred_bd()
                logger_exit.info("Actualizaciones: %s", 'rutina')

            else:
                    print("""
            Las credenciales ingresadas por el usuario
            No coinciden en su totalidad o son falsas.
            """)    
                    messagebox.showerror(title="Error crendenciales", message="Las credenciales son incorrectas")
                    logger_comun.error("Alguien ha ingresado las credenciales incorrectas.")
                    enviar_correo(contenido="Surgio una excepcion de tipo: ",error="CREDENCIALES FALSAS",asunto="Bot system error")
        except Exception as ErroPrincipal:
            messagebox.showerror(title="Credenciales", message="LAS CREDENCIALES NO COINCIDEN.")
            enviar_correo(contenido="Surgio una excepcion de tipo: ",error=ErroPrincipal,asunto="Bot system Error")
    except Exception as e:
        messagebox.showerror(title="Error de ejecución", message="No se pudo ejecutar el programa raiz.")
        enviar_correo(contenido="El programa no puede ejecutarse por fallo en el codigo o falta de dependencias.",
                      error=e, asunto="Bot System Error")
    
#     Principal.generar_html()