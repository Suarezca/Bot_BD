from datetime import datetime
import os

def logg_actions(mensaje):

    date_file = datetime.now().strftime('%m-%d-%Y')

    hora_fecha = datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")

    if os.path.exists(f"Logg/{date_file}"):

        with open(f"./Logg/{date_file}/Actions - {date_file}.log", "a") as file:

            file.writelines(f"{hora_fecha} --- {mensaje}\n")

        file.close()

    else:

        os.mkdir(f"Logg/{date_file}")

        with open(f"./logg/{date_file}/Actions - {date_file}.log", "a") as file:

            file.writelines(f"{hora_fecha} --- {mensaje}\n")

        file.close()

def logg_errors(mensaje):

    date_file = datetime.now().strftime('%m-%d-%Y')

    hora_fecha = datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")

    if os.path.exists(f"Logg/{date_file}"):

        with open(f"./Logg/{date_file}/Errors - {date_file}.log", "a") as file:

            file.writelines(f"{hora_fecha} --- {mensaje}\n")

        file.close()

    else:

        os.mkdir(f"Logg/{date_file}")

        with open(f"./logg/{date_file}/Errors - {date_file}.log", "a") as file:

            file.writelines(f"{hora_fecha} --- {mensaje}\n")

        file.close()