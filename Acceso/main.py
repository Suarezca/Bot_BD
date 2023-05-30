from selenium import webdriver
from selenium.webdriver.common.by import By
from tkinter import messagebox
from enviar_email import enviar_correo
import time
import keyboard
import requests, re, traceback, sys
from log import bitacora

#_-_-__-_-__-_-__-_-__-_-__-_-__-_-__-_-__-_-__-_-__-_-_
def get_credenciales(nombre_archivo): #Define a funcion, que toma el parámetro
    # Lee las credenciales de la base de datos desde el archivo especificado
    with open(nombre_archivo, "r") as f: #El archivo de abre en modo lectura y se cierra, al archivo se le asigna la variable f
        lines = f.readlines() #Lee todas las lineas del archivo y las guarda en la lista lines

    # Crea un diccionario a partir de las líneas del archivo
    credenciales = {}
    for line in lines: #Inicia el bucle for que recorre cada linea de la lista
        # Verifica que la línea contenga el carácter " "
        if " " not in line: 
            continue #Si no lo contiene pasa a la siguiente iteracion del bucle
        key, value = line.strip().split(" ") #Elimina espacios en blanco, divide la linea en dos partes y se asigna la variable Key y value
        credenciales[key] = value.strip() #se agrega una entrada al diccionario, clave es el valor de Key y valor es value

    return credenciales #Devuelve el diccionario que contiene las credenciales

def get_files(ruta, encoding='utf-8'): #Se define la funcion, toma dos parametros ruta y encoding con un valor predeterminado utf-8
    try:  #inicia bloque try-except, donde e ejecuta en try, pero si ocurre una excepcion se captura en el bloque except   
        with open(ruta, encoding=encoding, mode='r') as f: #abre el archivo, lee, el parametro encoding especifica la codificacion, se asigna la variable f
            return (True, f.read()) #si es exitoso, devuelve tupla de valor booleano true como primer elemento y el contenido del archivo con el metodo read() como segundo elemento
    except FileNotFoundError as e: #captura excepcion, y se le asigna la variable e
        error = str(e).split(': ') #se convierte la excepcion en una cadena de texto, se divide en dos, y se asigna a la variable error
        return (False, f'no se pudo abrir el archivo {error[1]}, {error[0]}') #si no puede abrir el archivo, devuelve valor booleano false como primer elemento y una cadena de texto que indica el error, con nombre de archivo y el tipo de error

class escribir(): #Se define la clase
    def __init__(self): #Se define el metodo de constructor de la clase
        self.caracteres = { #inicia diccionario con atributo self de la instancia actual de la clase
                ' ':'space',
                '\n':'enter',
                ';':'shift+;',
                '(':'shift+8',
                ')':'shift+9',      #caracteres especiales a utilizar
                '[':'shift+{',
                ']':'shift+}',
                '_':'shift+_',
                '=':'shift+0'
            }
    def escribir(self, texto): #se define el metodo, que toma parametro texto, se encarga de escribir mediante las combinaciones de teclas
        for char in texto: #Itera sobre cada carácter en el texto proporcionado como argumento
            keyboard.press_and_release(self.caracteres.get(char.lower(), char.lower())) #se utilizada modulo Keyboard para simulacion de pulsacion y liberacion de teclas correspondientes
            time.sleep(.2) #se pausa en 0.2 segundos entre cada pulsacion de tecla 


#_-_-__-_-__-_-__-_-__-_-__-_-__-_-__-_-__-_-__-_-__-_-_
class principal(): #Se define clase
    def __init__(self): #Se define el metodo, que es el constructor de la clase
        # Crea una instancia del navegador
        self.driver = webdriver.Chrome()

        # Maximizar la ventana del navegador
        self.driver.maximize_window()

        self.driver.implicitly_wait(10) #establece tiempo de espera de 10sg

    # compara el titulo de la pagina con un patron regular pasado por parametro
    def validar_titulo(self, titulo): #define la funcion que toma dos parametros
        new_titulo = self.driver.title #Obtiene el titulo de la pagina actual y lo asigna a la variable
        if re.match(titulo, new_titulo): #utiliza la funcion re.match del modulo re para comparar el patron regular con el titulo de la pagina y re.match busca coincidencia
            return True #si hay coincidencia devuelve true
        return False #si no hay coincidencia devuelve false

    def go_url(self, url, exp_url='', titulo=''): #Se define la funcion, donde se toma tres parametros
        res = True #Inicializa la variable, como true
        self.driver.get(url) #Se utiliza el tributo driver para acceder al metodo get y abrir el URL especifica
        self.driver.implicitly_wait(10) #se establece un tiempo de espera de 10sg
        # validar status por titulo o url esperados
        if exp_url: #verifica si la variable tiene un valor distinto de cadena vacia o false
            res = False #inicializa la variable como false
            nueva_url = self.driver.current_url #obtiene URL actual controlada por driber y guarda en la variable
            if exp_url in nueva_url: #verifica si el valor de exp_url esta presente en nueva_url
                res = True #actualiza el valor de res a true si se cumple
        if titulo: #verifica si la variable tiene valor distinto de una cadena vacia o false
            res = self.validar_titulo(titulo) #llama al metodo, pasando el valor titulo como argumento, el resultado de esta llamada se le asigna la variable res, actualizando su valor
        
        return res #retorna el valor res, que puede ser T o F dependiendo las condiciones verificadas
    
    def go_relative_url(self, *ruta): 
        current_url = self.driver.current_url # Obtiene la URL actual del navegador
        dominio = str(current_url).split('/phpMyAdmin/')[0] # Extrae el dominio de la URL actual
        ruta_all = dominio + ''.join(ruta) # Concatena el dominio con la ruta especificada
        titulo = f'^.* \/ .* \/ {ruta[-1]} \| phpMyAdmin.*$' # Crea un patrón de título esperado basado en la última parte de la ruta
        res=self.go_url(ruta_all, titulo=titulo)  # Navega a la URL completa y verifica el título esperado 
        return res # Retorna el resultado obtenido

            
    def inicio_sesion(self, user, password):
        # Ingresa las credenciales de inicio de sesión
        username_field = self.driver.find_element(By.NAME, value= 'user') # Encuentra el campo de nombre de usuario por su atributo "name"
        username_field.send_keys(user) # Ingresa el nombre de usuario en el campo correspondiente
        password_field = self.driver.find_element(By.NAME, value='pass') # Encuentra el campo de contraseña por su atributo "name"
        password_field.send_keys(password) # Ingresa la contraseña en el campo correspondiente

        # CLICK INICIAR SECION
        search_box = self.driver.find_element(by=By.ID, value='login_submit') # encuentra el elemento con el atributo ID y se guarda en la variable
        search_box.click() #Se realiza un clic en el elemento
        time.sleep(2) #espera 2sg antes de continuar

        res = self.validar_titulo('^.* \/ .* \| phpMyAdmin.*$')  #se llama el metodo, pasando como argumento la expresion regular y se guarda en la variable
        
        return res  #Se devuelve el valor almacenado en la variable res como resultado de la función
    
    # Click en boton sql
    def click_sql(self):
        click_sql = self.driver.find_element(by=By.XPATH, value='/html/body/div[5]/div/nav/div/ul/li[2]/a') #Se busca el elemento utilizando la ruta XPath especificada y se guarda en la variable 
        click_sql.click() #click en el elemento
        time.sleep(2) #espera 2 sg antes de continuar

    # Escribir rutina
    def print_sql(self, ruta):
        res = get_files(ruta)  #Se llama a la función get_files y se le pasa como argumento la ruta especificada. El resultado se guarda en la variable res
        if res[0]:    #Se verifica si el primer elemento de res es verdadero.
            esc = escribir()  #Se crea una instancia de la clase escribir y se guarda en la variable esc.
            esc.escribir(res[1]) #Se llama al método escribir de la instancia esc y se le pasa como argumento el segundo elemento de res
            self.save_click() #Se llama al método save_click del objeto actual.
        return res #Se retorna el valor de res
    
    # Oprimir boton continuar
    def save_click(self):
            save = self.driver.find_element(by=By.ID, value='button_submit_query') # encuentra el elemento con el atributo ID y se guarda en la variable
            # Hacer scroll hasta el elemento                 
            self.driver.execute_script("arguments[0].scrollIntoView();", save)
            time.sleep(1)
            save.click()
            
    def get_resultados(self):
        modificacion = False  #Se inicializa la variable modificacion con el valor False
        elementos = self.driver.find_elements(by=By.CSS_SELECTOR, value=".sql-highlight.cm-s-default") #Se busca y se obtienen todos los elementos que coinciden con el selector CSS 
        if elementos:
            modificacion = True  #se verifica si encuentra elementos, si hay se actuliza el valor
            for elemento in elementos:
                # Captura el texto de cada elemento
                texto = elemento.text

                # Formatea el mensaje de consulta buena
                mensaje_consulta = f"COMPLETO: {texto}"

                # Escribe el mensaje de consulta buena en la bitácora de consultas buenas
                bitacora.escribir_bitacora(mensaje_consulta, 'info')
        else:

            click_copy = self.driver.find_element(by=By.CSS_SELECTOR, value='.copyQueryBtn') #Se busca y se obtiene el elemento correspondiente al botón
            
            alerta = click_copy.get_attribute('data-text') #Se obtiene el texto asociado al atributo "data-text" del botón
            alerta2 = None
            elementos_xpath2 = self.driver.find_elements(by=By.XPATH, value='//*[@id="sqlqueryresultsouter"]/div/code') # Se inicializa la variable alerta2 y se buscan los elementos que representan los resultados de la consulta SQL mediante una expresión XPath
            if elementos_xpath2:
                alerta2 = elementos_xpath2[0].text #si se encuentra elementos, se obtiene el texto
                
            if alerta is not None and alerta2 is not None:  #Se verifica si tanto alerta como alerta2 tienen un valor distinto de None
                texto_completo = f'{alerta} {alerta2}' #Se crea una cadena de texto concatenando los valores de alerta y alerta2
                res = get_files('Configuraciones/rutinas.txt') # Se llama la funcion para obtener los datos del archivo y se guarda en la variable
                if res[0]: #verifica si el primer elemento es verdadero
                    rutinas = res[1].split('\n') #se divide el contenido del archivo por lineas y se guarda en la variable
                    for linea in rutinas:  #Se itera sobre cada línea en rutinas
                        if linea.upper() == alerta.upper():
                            break  # se compar cada linea, si hay coincidencia se sale del bucle
                        modificacion=True
                        mensaje_correcto = f"COMPLETADO: {linea}"
                        bitacora.escribir_bitacora(mensaje_correcto, 'info') #Se establece modificacion como verdadero y se registra un mensaje de éxito en la bitácora con el contenido de la línea
                    mensaje_error = f"Falló: {texto_completo}"
                    bitacora.escribir_bitacora(mensaje_error, 'error') #Si no se encuentra una coincidencia, se registra un mensaje de error en la bitácora con el contenido completo
        return modificacion #Se devuelve el valor

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
                                enviar_correo(contenido="Se realizaron nuevas actualizaciones a la Base de Datos, para más detalles ver informe",
                                        asunto="Bot Upgrade")
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