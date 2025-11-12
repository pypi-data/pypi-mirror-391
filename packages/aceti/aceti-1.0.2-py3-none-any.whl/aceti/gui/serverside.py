import os, sys, webbrowser, platform
import signal
import threading
import time
import traceback
import re
import pandas as pd
import urllib
from pathlib import Path
from datetime import datetime
import torch
import utm
import matplotlib.pyplot as plt
import numpy as np
from math import radians, cos, sin, sqrt, atan2
import cv2
from sqlalchemy import create_engine, text
from submodules.GPModels import GaussianProcessGPyTorch
from submodules.MQTT import MQTT
import json
import mysql.connector
import pymysql
pymysql.install_as_MySQLdb()
from time import sleep

# import machine this is for hard reset (machine.reset())
version = "1.0.0"
max_tab_idx = -1

class mysql_hdlr():
    def __init__(self,database):
        self.database=database
        self.table = "wqp_gaussian_maps"
        connect_str=f"mysql+mysqlconnector://root:{urllib.parse.quote_plus('azkenmugaÑ.')}@golem.us.es:6006/alec?charset=utf8mb4"
        # print(connect_str)        
        self.motor_mysql = create_engine(connect_str)

    def read_table(self, table):
        self.table=table
        try:
            with self.motor_mysql.connect() as conn:
                self.df = pd.read_sql_table(table, conn)
                self.dft=self.df.T
                print(f"table {self.database}.{self.table} loaded correctly")
        except:
            err=traceback.format_exc()
            print(f"table {self.database}.{self.table} is broken\n {err}")
            return
        
    def increase_max_message_size(self):
        cnx = mysql.connector.connect(user="root", password="azkenmugaÑ.", port="6006",
                                    host="golem.us.es", database="alec")
        # Crear un cursor
        cursor = cnx.cursor()

        # Ejecutar la consulta
        try:
            cursor.execute('SET GLOBAL max_allowed_packet=67108864')
        except:
            err=traceback.format_exc()
            print(f"limit augment failed: \n{err}")
            raise
        
        
    def query_db(self, query=None, database = "wqp"): #Query can also be Positions
        cnx = mysql.connector.connect(user="root", password="azkenmugaÑ.", port="6006",
                                    host="golem.us.es", database=database)
        # Crear un cursor
        cursor = cnx.cursor()

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

        aux_df = pd.DataFrame(results, columns=column_names)

        # Crear un DataFrame de pandas con los resultados

        if len(aux_df)==0:
            print(f"empty dataframe at {query}")
        else:
            print(f"queried {len(aux_df)} rows")

        return aux_df

        
    def load_df(self,df):
        self.df=df
        self.dft=df.T
        
    
    def overwrite(self, method = "append"):
        if method == "replace":
            print(f"start overwrite of table {self.table}")
        elif method == "append":
            print(f"adding new data to {self.table}")
        with self.motor_mysql.connect() as conn:
            self.df.to_sql(self.table, conn, if_exists=method, index=False)
        print("process done")

    def cleanup(self):
        print(f"cleaning table {self.table}")
        with self.motor_mysql.connect() as conn:
            with conn.begin():
                #borrar toda la tabla
                conn.execute(text(f"DELETE FROM {self.table}"))



class ACETI_SERVER():
    def __init__(self):
        #init SQL engine
        self.sql = mysql_hdlr("wqp_gaussian_maps")
        #init MQTT engine
        topics=["#"]
        self.mqtt= MQTT(on_message=self.on_message, 
                        topics2suscribe=topics)
        #init
        # Create folder path for data
        Path("data/GP_map/").mkdir(parents=True, exist_ok=True)

        self.sensors=['Conductivity', 'PH', 'Sonar', 'Temperature', 'Turbidity']
        
        mapas=["Alamillo", "Alamillo30x49", "AlamilloAccess11x15"]



        #para cada día y sensor generar un mapa
        days=self.sql.query_db(query= f"SELECT distinct DATE_FORMAT(Date, '%Y-%m-%d') FROM wqp.WQP WHERE Latitude<>0 AND Sensor='Conductivity' AND Data<>0;")
        #for each day
        first=True
        self.sql.cleanup()
        for i in days.values:    
            for mapa in mapas:        
                if mapa=="Alamillo":
                    self.scenario_map = np.genfromtxt(f"assets/Maps/alamillo.csv", delimiter=",")
                    self.map_coords = { 'lat_min': 37.417823087, 'lat_max': 37.421340387, 'lon_min': -6.001553482, 'lon_max': -5.997342323 }
                else:
                    self.latlonmap = np.load(resource_path(f"assets/Maps/{mapa}latlon.npy"), allow_pickle=True)
                    self.scenario_map = np.load(resource_path(f"assets/Maps/{mapa}mask.npy"), allow_pickle=True)
                    self.map_coords = { 'lat_min': self.latlonmap[-1,-1,0], 'lat_max': self.latlonmap[0,0,0], 'lon_min': self.latlonmap[0,0,1], 'lon_max': self.latlonmap[-1,-1,1] }

                self.pos_ini = utm.from_latlon(self.map_coords['lat_min'], self.map_coords['lon_min'])

                #get map shape
                self.rows, self.cols = self.scenario_map.shape
                self.res_lat, self.res_lon = (self.map_coords['lat_max'] - self.map_coords['lat_min']) / self.rows, (self.map_coords['lon_max'] - self.map_coords['lon_min']) / self.cols
                aux_df=self.generate_maps(self.sql.query_db(query=f"SELECT * FROM wqp.WQP where date(Date) = '{i[0]}' AND Latitude<>0 AND Longitude<>0;", database="wqp"))
                aux_df = aux_df.assign(Date=i[0])
                aux_df = aux_df.assign(mapa=mapa)
                if False:
                    #crear un database auxiliar con meanmap y sensor
                    aux_df2=aux_df[aux_df["mean_map"].notnull()][["mean_map", "sensor"]]
                    #guardar aux_df2 en un csv
                    aux_df2.to_csv(f"data/GP_map/{i[0]}.csv", index=False)
                    exit()
                max_size=200 #we will send packet by packet
                for j in range(np.ceil(len(aux_df)/max_size).astype(int)):
                    transmitable_df=aux_df[j*max_size:min((j+1)*max_size, len(aux_df))]
                    self.sql.load_df(transmitable_df)
                    if first:
                        first=False
                        self.sql.overwrite(method="replace")
                    else:
                        self.sql.overwrite(method="append")
                # transmitable_df=aux_df[(len(aux_df)-max_size):]
                # self.sql.load_df(transmitable_df)
                # self.sql.overwrite(method="append")

            


    
    def generate_maps(self, df, rewrite=False):
        # Convertir las coordenadas GPS a metros respecto al inicio de la imagen con la función haversine
        df_=pd.DataFrame()
        for sensor in self.sensors:
            aux_df=pd.DataFrame()
            sensor_df = df[df['Sensor'] == sensor].reset_index(drop=True)
            
            # Quitar las medidas con valor cero
            sensor_df = sensor_df[sensor_df['Data'] != 0].reset_index(drop=True)
            sensor_df=sensor_df.drop(columns=["Sensor"])

            # Limpiar outliers
            Q1 = sensor_df['Data'].quantile(0.25)
            Q3 = sensor_df['Data'].quantile(0.75)
            IQR = Q3 - Q1
            sensor_df = sensor_df[~((sensor_df['Data'] < (Q1 - 3 * IQR)) | (sensor_df['Data'] > (Q3 + 3 * IQR)))]

            sensor_df["Latitude"] = np.ceil((sensor_df["Latitude"].astype(float).values* 10000))/10000 -0.00005
            sensor_df["Longitude"] = np.ceil((sensor_df["Longitude"].astype(float).values* 10000))/10000 -0.00005

            positions = sensor_df.groupby(['Latitude', 'Longitude']).mean()

            y, x = zip(*[self.gps_to_matrix_idx(lat, lon, self.map_coords['lat_max'], self.map_coords['lon_min'], self.res_lat, self.res_lon) for lat, lon in positions.index.values])
            xy = list(zip(y, x)) # Pares de coordenadas GPS
            aux_df["x"]=x
            aux_df["y"]=y
            aux_df["x"]=aux_df["x"].astype(int)
            aux_df["y"]=aux_df["y"].astype(int)


            data = [float(positions["Data"].loc[row]) for row in positions.index.values]
            data=np.array(data)

            if sensor == 'Sonar':# Pasar a metros
                data = data / 1000

            gaussian_process = GaussianProcessGPyTorch(scenario_map = self.scenario_map, initial_lengthscale = 300, kernel_bounds = (200, 400), training_iterations = 50, scale_kernel=True, device = 'cuda' if torch.cuda.is_available() else 'cpu', mean = data.mean())
            gaussian_process.fit_gp(X_new=xy, y_new=data, variances_new=[0.005]*len(data))

            mean_map, uncertainty_map = gaussian_process.predict_gt()
            list_mean_map =  mean_map.tolist()
            str_mean_map = map(str, list_mean_map)
            aux_df=pd.concat([aux_df, pd.DataFrame(data={"mean_map" : str_mean_map})], axis=1)

            # aux_df=pd.concat([aux_df, pd.DataFrame(data={"uncertainty_map" : np.asarray(uncertainty_map).flatten()})], axis=1)
            aux_df=aux_df.assign(sensor= sensor)
            # self.create_map(mean_map, uncertainty_map, x, y, sensor=sensor)

            df_=pd.concat([df_, aux_df], ignore_index = True)

        return df_

    def create_map(self, mean_map, uncertainty_map, x, y, sensor="Conductivity"):

        plt.clf()
        # fig, axis = plt.subplots()
        # Punto de despliegue
        # plt.text(350, 1100, 'Punto de despliegue', fontsize=9, rotation=0, ha='center', va='center', color='w')
        # plt.scatter(175, 1050, c='r', s=50, marker='X', zorder=2)
        plt.xticks([])
        plt.yticks([])

        # Contorno
        cs_internos = plt.contour(mean_map, colors='black', alpha=0.7, linewidths=0.7, zorder=1)
        cs_externo = plt.contour(mean_map, colors='black', alpha=1, linewidths=1.7, zorder=1)

        cs_internos.collections[0].remove()
        for i in range(1, len(cs_externo.collections)):
            cs_externo.collections[i].remove()
        plt.clabel(cs_internos, inline=1, fontsize=3.5)

        # Mapa y puntos de muestreo
        plt.scatter(x, y, c='black', s=1, marker='.', alpha=0.5)
        # vmin_dict = {'Sonar': 2, 'Conductivity': 2.29, 'PH': 7.48, 'Temperature': 17.1, 'Turbidity': 30}
        # vmax_dict = {'Sonar': 0.5, 'Conductivity': 2.14, 'PH': 7.16, 'Temperature': 14.50, 'Turbidity': 15}
        # plt.imshow(mean_map, cmap='viridis', alpha=1, origin='upper', vmin=vmin_dict[sensor], vmax=vmax_dict[sensor])
        vmin = np.min(mean_map[mean_map > 0])
        vmax = np.max(mean_map[mean_map > 0])
        plt.imshow(mean_map, cmap='viridis', alpha=1, origin='upper', vmin=vmin, vmax=vmax)

        # Recortar el mapa
        # plt.ylim(1150, 200)

        # Leyendas
        unidades_dict = {'Sonar': 'Profundidad (m)', 'Conductivity': 'Conductividad (mS/cm)', 'PH': 'pH', 'Temperature': 'Temperatura (ºC)', 'Turbidity': 'Turbidez (NTU)'}
        nombre_dict = {'Sonar': 'Batimetría', 'Conductivity': 'Conductividad', 'PH': 'pH', 'Temperature': 'Temperatura', 'Turbidity': 'Turbidez'}
        plt.colorbar(shrink=0.65).set_label(label=unidades_dict["Conductivity"],size=12)#,weight='bold')
        # plt.text(1950, 650, unidades_dict[sensor], fontsize=12, rotation=90, ha='center', va='center', color='k')
        plt.title(f'{nombre_dict[sensor]} del Lago Mayor (Parque del Alamillo)')
        # if(not os.path.exists("outs")):
        #     os.makedirs("outs")
        # savepath=self.resource_path(f"outs/{nombre_dict[sensor]}_{self.selected_map}.pdf")
        # plt.savefig(savepath, format='pdf')
        plt.show()


    def mainloop(self):
        # query=f"SELECT * FROM wqp.WQP where date(Date) = '{date_}' AND Latitude<>0 AND Sensor='{self.taget_sensor}';"
        sleep(2)



    def dummy(self):
        pass

    def on_message(self, _client, user_data, msg):
        try:
            if "asv_state" in msg.topic:
                self.last_message=json.loads(msg.payload)
            elif "database/wqp" in msg.topic:
                pass
        except:
            error= traceback.format_exc()
            print(f"There was an error parsing mqtt \n{error}")


    def haversine(self, lat1, lon1, lat2, lon2):
        # Radio de la Tierra en kilómetros
        R = 6371.0
        
        # Convertir coordenadas de grados a radianes
        lat1_rad = radians(lat1)
        lon1_rad = radians(lon1)
        lat2_rad = radians(lat2)
        lon2_rad = radians(lon2)
        
        # Diferencias de coordenadas
        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad
        
        # Fórmula del haversine
        a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        # Distancia total en kilómetros
        distance = R * c * 1000
        return distance
    
    def gps_to_matrix_idx(self, lat, lon, lat_max, lon_min, res_lat, res_lon):

        row_idx = int((lat_max - lat) / res_lat)
        col_idx = int((lon - lon_min) / res_lon)

        # Limitar los índices dentro de los rangos válidos de la matriz
        # row_idx = max(0, min(row_idx, rows - 1))
        # col_idx = max(0, min(col_idx, cols - 1))

        return row_idx, col_idx


def resource_path(relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)


def main(args=None):
    server=ACETI_SERVER()
    print(f"Init Version {version}")
    server.mainloop() 
    print("Finishing Application")
    server.mqtt.close()
    print("Application Finished")
    
if __name__ == '__main__':
    main()
