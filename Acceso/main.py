from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tkinter import messagebox
from enviar_email import enviar_correo
import time
import keyboard
# import configparser
import requests, re, traceback, sys
# import logging
import datetime
# from selenium.common.exceptions import WebDriverException
# import os
# from bs4 import BeautifulSoup
# from Logg import logg_actions, logg_errors
# from datetime import datetime

from log import bitacora

#_-_-__-_-__-_-__-_-__-_-_otro archivo_-_-__-_-__-_-__-_-__-_-__-_-_
def get_credenciales(nombre_archivo):
    # Lee las credenciales de la base de datos desde el archivo especificado
    with open(nombre_archivo, "r") as f:
        lines = f.readlines()

    # Crea un diccionario a partir de las líneas del archivo
    credenciales = {}
    for line in lines:
        # Verifica que la línea contenga el carácter " "
        if " " not in line:
            continue
        key, value = line.strip().split(" ")
        credenciales[key] = value.strip()

    return credenciales

def get_files(ruta, encoding='utf-8'):
    try:     
        with open(ruta, encoding=encoding, mode='r') as f:
            return (True, f.read())
    except FileNotFoundError as e:
        error = str(e).split(': ')
        return (False, f'no se pudo abrir el archivo {error[1]}, {error[0]}')

class escribir():
    def __init__(self):
        self.caracteres = {
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
    def escribir(self, texto):
        for char in texto:
            keyboard.press_and_release(self.caracteres.get(char.lower(), char.lower()))
            time.sleep(.2)


#_-_-__-_-__-_-__-_-__-_-_otro archivo_-_-__-_-__-_-__-_-__-_-__-_-_
class principal():
    def __init__(self):
        # Crea una instancia del navegador
        self.driver = webdriver.Chrome()

        # Maximizar la ventana del navegador
        self.driver.maximize_window()

        self.driver.implicitly_wait(10)

    # compara el titulo de la pagina con un patron regular pasado por parametro
    def validar_titulo(self, titulo):
        new_titulo = self.driver.title
        if re.match(titulo, new_titulo):
            return True
        return False

    def go_url(self, url, exp_url='', titulo=''):
        res = True
        self.driver.get(url)
        self.driver.implicitly_wait(10)
        # validar status por titulo o url esperados
        if exp_url:
            res = False 
            nueva_url = self.driver.current_url
            if exp_url in nueva_url:
                res = True
        if titulo:
            res = self.validar_titulo(titulo)
        
        return res
    
    def go_relative_url(self, *ruta):
        current_url = self.driver.current_url
        dominio = str(current_url).split('/phpMyAdmin/')[0]
        ruta_all = dominio + ''.join(ruta)
        titulo = f'^.* \/ .* \/ {ruta[-1]} \| phpMyAdmin.*$'
        res=self.go_url(ruta_all, titulo=titulo)   
        return res

            
    def inicio_sesion(self, user, password):
        # Ingresa las credenciales de inicio de sesión
        username_field = self.driver.find_element(By.NAME, value= 'user')
        username_field.send_keys(user)
        password_field = self.driver.find_element(By.NAME, value='pass')
        password_field.send_keys(password)

        # CLICK INICIAR SECION
        search_box = self.driver.find_element(by=By.ID, value='login_submit')
        search_box.click()
        time.sleep(2)

        res = self.validar_titulo('^.* \/ .* \| phpMyAdmin.*$')
        
        return res
    
    # Click en boton sql
    def click_sql(self):
        click_sql = self.driver.find_element(by=By.XPATH, value='/html/body/div[5]/div/nav/div/ul/li[2]/a')
        click_sql.click()
        time.sleep(2)

    # Escribir rutina
    def print_sql(self, ruta):
        res = get_files(ruta)
        if res[0]:    
            esc = escribir()
            esc.escribir(res[1])
            self.save_click()
        return res
    
    # Oprimir boton continuar
    def save_click(self):
            save = self.driver.find_element(by=By.XPATH, value='/html/body/div[7]/form/div/div[3]/div/div[6]/input')
            # Hacer scroll hasta el elemento
            self.driver.execute_script("arguments[0].scrollIntoView();", save)
            time.sleep(1)
            save.click()
            
    def get_resultados(self):
        modificacion = False
        elementos = self.driver.find_elements(by=By.CSS_SELECTOR, value=".sql-highlight.cm-s-default")
        if elementos:
            modificacion = True
            for elemento in elementos:
                # Captura el texto de cada elemento
                texto = elemento.text

                # Formatea el mensaje de consulta buena
                mensaje_consulta = f"COMPLETO: {texto}"

                # Escribe el mensaje de consulta buena en la bitácora de consultas buenas
                bitacora.escribir_bitacora(mensaje_consulta, 'info')
        else:
            # Intenta capturar el texto de los elementos XPath originales
            click_copy = self.driver.find_element(by=By.CSS_SELECTOR, value='.copyQueryBtn')
            
            alerta = click_copy.get_attribute('data-text')
            alerta2 = None
            elementos_xpath2 = self.driver.find_elements(by=By.XPATH, value='//*[@id="sqlqueryresultsouter"]/div/code')
            if elementos_xpath2:
                alerta2 = elementos_xpath2[0].text
                
            if alerta is not None and alerta2 is not None:
                texto_completo = f'{alerta} {alerta2}'
                res = get_files('Configuraciones/rutinas.txt')
                if res[0]:
                    rutinas = res[1].split('\n')
                    for linea in rutinas:
                        if linea.upper() == alerta.upper():
                            break
                        modificacion=True
                        mensaje_correcto = f"COMPLETADO: {linea}"
                        bitacora.escribir_bitacora(mensaje_correcto, 'info')
                    mensaje_error = f"Falló: {texto_completo}"
                    bitacora.escribir_bitacora(mensaje_error, 'error')
        return modificacion

if __name__ == "__main__":

    try: 
        url = "http://henry-sanchez.com/gbm/verificationcode/codes.txt"
        #config = configparser.ConfigParser()
        response = requests.get(url)
        contenido = response.text

        codigo_verificacion = re.findall(r".*(?:\w*?|\d*?|\$*?|\#*?|\&*?|\%*?|\-*?)\S", contenido)
        
        codigo_usuario = 'AX&23#NL98'#input("Ingrese codigo de verificación: -- ")
        if codigo_usuario in codigo_verificacion:
            bitacora.escribir_bitacora('Inicio exitoso', 'info')

            # obtener credenciales en diccionario
            credenciales = get_credenciales("Configuraciones/credenciales_bd.txt")
            navegador = principal()
            
            if not navegador.go_url(credenciales['host'], exp_url='phpMyAdmin/index.php'):
                print("Error: Direccion de host no valida")
                bitacora.escribir_bitacora(f'La direccion del host no es valida para login con phpMyAdmin', 'error')
                enviar_correo(contenido="Ocurrio un error al intentar abrir el host",
                              asunto="Bot System Error")
            else:
                if not navegador.inicio_sesion(credenciales['user'], credenciales['password']):
                    print("Error: Ocurrio un error al intentar iniciar sesion")
                    bitacora.escribir_bitacora(f'Credenciales incorrectas, no se pudo iniciar sesión', 'error')
                    enviar_correo(contenido="Ocurrio un error al intentar iniciar sesion",
                                    asunto="Bot System Error")
                else:
                    if not navegador.go_relative_url(f'/phpMyAdmin/index.php?route=/database/structure&db=', credenciales["bd_name"]):
                        messagebox.showerror(title="Abrir base datos", message="No es posible abrir la BD, revise los parametros")
                        enviar_correo(contenido="No se encontro la base de datos especificada",
                                    asunto="Bot system error")
                    else:
                        navegador.click_sql()
                        res = navegador.print_sql(ruta='Configuraciones/rutinas.txt')
                        if not res[0]:
                            print(res[1])
                            bitacora.escribir_bitacora(res[1], 'error')
                            enviar_correo(contenido="Ocurrio un error al obtener archivo rutina",
                                        asunto="Bot System Error")
                        else:
                            res = navegador.get_resultados()
                            if res:
                                print('notificacion de modificaciones enviada :)')

        else:
                print("""
        Las credenciales ingresadas por el usuario
        No coinciden en su totalidad o son falsas.
        """)    
                messagebox.showerror(title="Error crendenciales", message="Las credenciales son incorrectas")
                bitacora.escribir_bitacora("Alguien ha ingresado las credenciales incorrectas.", 'error')
                enviar_correo(contenido="Surgio una excepcion de tipo: CREDENCIALES FALSAS",asunto="Bot system Error")
    except Exception as e:
        messagebox.showerror(title="Error de ejecución", message="Ha ocurrido un error en la ejecucion, se envio un reporte")
        enviar_correo(contenido="Ocurrio un error durante la ejecucion para mas detalles, consulte el informe generado",
                      asunto="Bot System Error")
        linea = traceback.extract_tb(sys.exc_info()[2])[-1]
        bitacora.escribir_bitacora(f"Archivo: {linea.filename}, línea: {linea.lineno}, función: {linea.name}, código: {linea.line}", 'error')
        print(e)
        
    bitacora.gen_html()