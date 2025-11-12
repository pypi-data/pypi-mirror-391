import pandas as pd
import mysql.connector
import os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import threading
import sys
import tkinter
import traceback
from math import radians, cos, sin, sqrt, atan2
import matplotlib.pyplot as plt
# import seaborn as sns
sys.path.append('../')

class Database():
    def __init__(self, selected_map = 'alamillo'):
        self.sensors=['Conductivity', 'PH', 'Sonar', 'Temperature', 'Turbidity']
        self.user="readonly"
        self.password="aceti"
        self.host="golem.us.es"
        self.selected_map = selected_map
        self.busy=False
        self.sensor_maps={}

    def query(self, date='2024-02-27', table="WQP", query = None, save=True,  database = "wqp"):
        if not self.busy:
            #execute in a thread
            # start=datetime.now()
            querythread=threading.Thread(target=self.__query,args=(date, table, query, save, database))
            self.busy=True
            querythread.start()
            # afterquery=datetime.now()
            # difference = afterquery - start
            # seconds_in_day = 24 * 60 * 60
            # aux=divmod(difference.days * seconds_in_day + difference.seconds, 60)
            # print(f"query delayed {aux[0]} minutes {aux[1]} seconds")

    def __query(self, date='2024-02-27', table="WQP", query=None, save =False, database = "wqp"): #Query can also be Positions
        self.date=date
        try:
            cnx = mysql.connector.connect(user=self.user, password=self.password, port="6006",
                                        host=self.host, database=database, connection_timeout=2)
        except:
            tkinter.messagebox.showerror(title="Mysql Connector", message="database connection failed, check your internet connection and whether US ports are open",)
            return
        # Crear un cursor
        cursor = cnx.cursor()
        # Definir la consulta SQL con el filtro de fecha
        # query = "SELECT * FROM ASV_US.ASV WHERE date(Date) >= '2024-02-16' AND date(Date) <= '2024-02-15'"
        if query is None:
            if table == "WQP":
                query = f"SELECT * FROM wqp.{table} where date(Date) = '{date}' AND Latitude<>0 AND Longitude<>0;"
            else:
                query = f"SELECT * FROM wqp.{table} where date(Date) = '{date}' AND Latitude<>0 AND Longitude<>0;"

        # Ejecutar la consulta
        try:
            cursor.execute(query)
        except:
            err=traceback.format_exc()
            print(f"query {query} failed: \n{err}")
            raise

        # Obtener nombres de columnas
        column_names = cursor.column_names

        # Obtener los resultados
        results = cursor.fetchall()

        # Cerrar el cursor y la conexión a la base de datos
        cursor.close()
        cnx.close()

        # Crear un DataFrame de pandas con los resultados
        self.df = pd.DataFrame(results, columns=column_names)

        if len(self.df)==0:
            self.busy=False
            print(f"empty dataframe at {date}")
            return

        print(f"queried {len(self.df)} rows")
        self.busy=False

    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def refresh_dates(self, table="WQP", database="wqp"):
        try:
            cnx = mysql.connector.connect(user=self.user, password=self.password, port="6006",
                                        host=self.host, database=database, connection_timeout=2)
        except:
            tkinter.messagebox.showerror(title="Mysql Connector", message="database connection failed, check your internet connection and whether US ports are open",)
            return
        # Crear un cursor
        cursor = cnx.cursor()
        # Definir la consulta SQL con el filtro de fecha
        # query = "SELECT * FROM ASV_US.ASV WHERE date(Date) >= '2024-02-16' AND date(Date) <= '2024-02-15'"
        if table == "WQP":
            query = f"SELECT distinct DATE_FORMAT(Date, '%Y-%m-%d') FROM wqp.{table} WHERE Latitude<>0 AND Sensor='Conductivity' AND Data<>0;"
        elif table == "OBJECT_POSITION":
            query = f"SELECT distinct DATE_FORMAT(Date, '%Y-%m-%d') FROM wqp.{table} WHERE Latitude_Obj<>0;"
        elif table == "PATHS":
            query = f"SELECT distinct DATE_FORMAT(Date, '%Y-%m-%d') FROM wqp.{table} WHERE Latitude<>0;"
        else:
            query = f"SELECT distinct DATE_FORMAT(Date, '%Y-%m-%d') FROM {database}.{table};"

        # Ejecutar la consulta
        cursor.execute(query)

        # Obtener nombres de columnas
        column_names = cursor.column_names

        # Obtener los resultados
        results = cursor.fetchall()

        # Cerrar el cursor y la conexión a la base de datos
        cursor.close()
        cnx.close()

        # Crear un DataFrame de pandas con los resultados
        self.date_df = pd.DataFrame(results, columns=column_names)
        self.date_df = self.date_df[column_names[0]]
        if len(self.date_df)==0:
            self.busy=False
            print(f"there are no data from {table} at any date")
            return
        print(f"found {len(self.date_df)} dates with data")

    def refresh_maps(self, database="alec"):
        try:
            cnx = mysql.connector.connect(user=self.user, password=self.password, port="6006",
                                        host=self.host, database=database, connection_timeout=2)
        except:
            tkinter.messagebox.showerror(title="Mysql Connector", message="database connection failed, check your internet connection and whether US ports are open",)
            return
        # Crear un cursor
        cursor = cnx.cursor()
        query = f"SELECT distinct mapa FROM {database}.wqp_gaussian_maps;"

        # Ejecutar la consulta
        cursor.execute(query)

        # Obtener nombres de columnas
        column_names = cursor.column_names

        # Obtener los resultados
        results = cursor.fetchall()

        # Cerrar el cursor y la conexión a la base de datos
        cursor.close()
        cnx.close()

        # Crear un DataFrame de pandas con los resultados
        map_df = pd.DataFrame(results, columns=column_names)
        map_df = map_df["mapa"]
        if len(map_df)==0:
            self.busy=False
            print(f"there are no maps at any date")
            return
        print(f"found {len(map_df)} maps with data")
        return map_df.values
        
        