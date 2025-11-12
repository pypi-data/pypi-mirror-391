import tkinter
import tkinter.font
import tkinter.ttk
import os, sys
from tkintermapview import TkinterMapView
from datetime import datetime, date
import gc
import traceback
import numpy as np
import json
sys.path.append('../')
from ..shared import *
from ..assets import *
from ..submodules.database import Database
from ..submodules.MQTT import *
from ..widgets.labels import *
from ..widgets.highlable_calendar import *
from ..widgets.map_markers import *
from ..widgets.checkbox import *



class MISSIONTAB(tkinter.ttk.PanedWindow):
    def __init__(self, parent=None):
        if parent is None:
            parent=tkinter.Tk()
        self.parent=parent
        self.trash_markers=[]
        #inherit
        try:
            self.assets=self.parent.assets
            self.shared=self.parent.shared
        except:
            self.assets=Assets()
            self.shared=SHARED()
        
        self.database= Database()
        self.busy=False
        self.mission_loop_object = None
        self.date=date.today()
        self.on_status=True
        self.taget_sensor=self.database.sensors[0]
        self.now_status=True
        self.refreshed = False
        self.waiting=False
        
        super().__init__(orient="horizontal")

        self.mission_tab()
        # self.playback_data()

        self.ships=[SHIP("vehicle_1", 0.0, 0.0, parent=self)]
        self.last_message=json.loads('{"Latitude" : 0.0 , "Longitude" : 0.0 , "Heading" : 0.0}')
        topics=["#"]

        self.mqttConnection = MQTT( on_message=self.on_message, 
                                    topics2suscribe=topics
                                    )

    def mission_tab(self):
        self.GPS_panel = tkinter.ttk.PanedWindow(orient="vertical", width=int(self.parent.screenwidth*0.8))
        self.add(self.GPS_panel)

        
        #create map
        self.map_widget = TkinterMapView(corner_radius=0, height=int(self.parent.screenheight*0.75)+1, database_path=self.assets.map_tiles) #this widget has no automatic size
        self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        self.GPS_panel.add(self.map_widget)
        self.topleft=[37.420088,-6.001346]
        self.bottomright=[37.418399,-5.997504]
        self.map_widget.fit_bounding_box(self.topleft, self.bottomright)


        self.measures=[]
        self.ships=[]

        ##create info bar
        gps_data= tkinter.ttk.PanedWindow(orient="horizontal",height=1)
        self.GPS_panel.add(gps_data)
        #last value frame
        self.sensordata = tkinter.Frame(gps_data)
        Sensors=["Turbidity", "PH", "Battery", "Temperature", "Conductivity", "Sonar"]
        aux=create_labelh_with_units(self.sensordata, "Turbidity", self.shared.Turbidity, "NTU", expand="true")
        aux=create_labelh(self.sensordata, "PH", self.shared.PH, expand="true")
        aux=create_labelh_with_units(self.sensordata, "Battery:", self.shared.Battery, "%", expand="true")
        aux=create_labelh_with_units(self.sensordata, "Temperature:", self.shared.Temperature, "ºC", expand="true")
        aux=create_labelh_with_units(self.sensordata, "Conductivity:", self.shared.Conductivity, "S/cm", expand="true")
        aux=create_labelh_with_units(self.sensordata, "Sonar:", self.shared.Sonar, "m", expand="true")
        aux=create_labelh(self.sensordata, "Date:", self.shared.Date, expand="true")
        self.sensordata.pack(side="left",expand="true",fill="both")
        self.after_object=None
        
        #play and center buttons
        buttonsframe=tkinter.Frame(gps_data, height=1, borderwidth=1) #for date and play/center
        self.center_buttom = tkinter.Button(buttonsframe, text="Center", command=self.center_map, width=20, height=1,font=tkinter.font.Font(weight='bold', size=18))
        self.center_buttom.pack(side="left",expand="false",fill="y")
        buttonsframe.pack(side="right",expand="false",fill="y")

        #map selection
        self.map_selection=tkinter.Frame(self, width=20)
        self.map_selection.pack_propagate(False)
        self.add(self.map_selection)

        self.checkboxes=[]
        for i in range(len(self.database.sensors)): #for as many sensors
            aux= Checkbox(self.map_selection, text=self.database.sensors[i], width=20, command=lambda a=i: self.draw_map(a))
            aux.pack(side="top")
            self.checkboxes.append(aux)
        self.checkboxes[0].check()

        self.playback_frame=tkinter.Frame(self.map_selection)
        self.playback_button = tkinter.Button(self.playback_frame, image = self.assets.icon_off, bd = 0, command = self.playback_data)
        self.playback_label=tkinter.Label(self.playback_frame, text="On ")
        self.playback_label.pack(side="left", anchor="e")
        self.playback_button.pack(side="left", pady = 50, anchor="w")
        self.playback_frame.pack(side="top", fill="x")

        #calendar
        self.playback_selector_frame=tkinter.Frame(self.map_selection)
        self.cal = highlable_calendar(self.playback_selector_frame, selectmode = 'day', parent=self)
        self.cal.selection_set(self.date)
        # self.parent.bind("<<UpdatePlotData>>", self.download_database)
        self.cal.pack(pady = 20, expand="false",fill="none")
        self.refresh_buttom = tkinter.Button(self.playback_selector_frame, text="refresh", command=self.refresh_database, width=8, height=1,font=tkinter.font.Font(weight='bold', size=18))
        self.refresh_buttom.pack(side="top",expand="false",fill="x")


        self.playback_selector_frame.pack()
        
        self.data_points_label=tkinter.IntVar()
        a= tkinter.Frame(self.map_selection, padx=10, pady=2)
        a.pack(side='top', fill='both', expand=True,)
        a.pack_propagate(False)
        tkinter.Label(a, text="Number of Points", font=tkinter.font.Font(weight='bold')).pack(side="left", fill='both', padx=0, pady=2)
        tkinter.Label(a, textvariable=self.data_points_label).pack(side="left", fill='both', padx=0, pady=2)

        self.status_label=tkinter.StringVar()
        a= tkinter.Frame(self.map_selection, padx=10, pady=2)
        a.pack(side='top', fill='both', expand=True,)
        a.pack_propagate(False)
        tkinter.Label(a, text="Status", font=tkinter.font.Font(weight='bold')).pack(side="left", fill='both', padx=0, pady=2)
        tkinter.Label(a, textvariable=self.status_label).pack(side="left", fill='both', padx=0, pady=2)
        self.status_label.set("Off")


    def center_map(self,event=None):
        self.map_widget.fit_bounding_box(self.topleft, self.bottomright)


    def playback_data(self, event=None):
        self.on_status = not self.on_status
        #TODO: change to data from specific date or now
        if not self.on_status:
            self.after_object = self.parent.after(500, self.refresh_particles)
            self.playback_button.config(image=self.assets.icon_on)
        else:
            if self.after_object != None:
                self.parent.after_cancel(self.after_object)
            self.after_object=None
            self.playback_button.config(image=self.assets.icon_off)
            self.status_label.set("Off")
    
    def refresh_database(self, event=None):
        self.database.refresh_dates(table="PATHS")
        self.cal.unhighlight()
        for _date in self.database.date_df:
            dat=date.fromisoformat(_date)
            self.cal.add_to_data(dat)
        self.refreshed = True

    def refresh_particles(self):
        if self.on_status ==True:
            return
        if not self.database.busy and self.waiting==False:
            self.status_label.set("Querying")
            date_=self.cal.selection_get().strftime("%Y-%m-%d")
            # query=f"SELECT * FROM wqp.OBJECT_POSITION where date(Date) = '{date_}';"
            query=f"SELECT Latitude,Longitude,Data FROM wqp.WQP where date(Date) = '{date_}' AND Latitude<>0 AND Sensor='{self.taget_sensor}';"
            self.database.query(query=query) #self.date.strftime("2024-02-27")
            self.waiting=True
        if self.database.busy:
            self.after_object = self.parent.after(1000, self.refresh_particles)
            return
        self.waiting=False
        if(len(self.database.df) == 0):
            self.status_label.set("No Data")
            self.data_points_label.set(0)

            self.after_object = self.parent.after(8000, self.refresh_particles)
            return
        self.status_label.set("Printing")

        data = self.database.df[self.database.df['Data'] != 0]
        self.data_points_label.set(len(data))
        data["Latitude"] = np.ceil((data["Latitude"].astype(float).values* 10000))/10000 -0.00005
        data["Longitude"] = np.ceil((data["Longitude"].astype(float).values* 10000))/10000 -0.00005

        if True: #calculate mean
            positions = data.groupby(['Latitude', 'Longitude']).mean()
            print(f"there are {len(positions)} different positions")

            self.map_widget.delete_all_marker()
            del self.ships
            del self.measures
            gc.collect()
            self.ships=[]
            self.measures=[]
            expected_min=positions["Data"].min()
            expected_range=positions["Data"].max()-expected_min +0.001 #avoid division by 0
            print(f"we are expecting an measure between {positions['Data'].max()} and {positions['Data'].min()}")
            for row in positions.index.values:
                self.measures.append(MEASURE(float(positions["Data"].loc[row]), float(row[0]), float(row[1]), parent=self, range_=expected_range, min_=expected_min))
            self.after_object = self.parent.after(8000, self.refresh_particles)
        else:
            positions = data[['Latitude', 'Longitude']].drop_duplicates()
            self.map_widget.delete_all_marker()
            self.ships=[]
            self.measures=[]
            expected_min=positions["Data"].min()
            expected_range=positions["Data"].max()-expected_min +0.001 #avoid division by 0
            print(f"we are expecting an measure between {positions['Data'].max()} and {positions['Data'].min()}")
            for row in positions.index.values:
                self.measures.append(MEASURE(float(data["Data"].loc[row]), float(data["Latitude"].loc[row]), float(data["Longitude"].loc[row]), parent=self, range_=expected_range, min_=expected_min))
            self.after_object = self.parent.after(15000, self.refresh_particles)
        self.status_label.set(f"Iddle {self.taget_sensor}")

    def close(self):
        # ensure playback loop is stopped and any after callback cancelled
        try:
            if self.on_status==False:
                self.playback_data()
        except Exception:
            pass
        try:
            if hasattr(self, 'after_object') and self.after_object:
                self.parent.after_cancel(self.after_object)
                self.after_object = None
        except Exception:
            pass
        # attempt to destroy map widget and free resources
        try:
            if hasattr(self, 'map_widget') and self.map_widget is not None:
                try:
                    self.map_widget.delete_all_marker()
                except Exception:
                    pass
                try:
                    self.map_widget.destroy()
                except Exception:
                    pass
                self.map_widget = None
        except Exception:
            pass

    def open(self):
        if not self.refreshed:
            self.refresh_database()

    def on_message(self, _client, user_data, msg):
        try:
            if "asv_state" in msg.topic:
                self.last_message=json.loads(msg.payload)
                if len(self.ships)>0:
                    self.ships[0].update_rotation(-self.last_message['Heading'])
                    self.ships[0].set_position(self.last_message["Latitude"], self.last_message["Longitude"])
                else:
                    self.ships.append(SHIP("vehicle_1", self.last_message["Latitude"], self.last_message["Longitude"], heading=-self.last_message['Heading'], parent=self))
            elif "database/wqp" in msg.topic:
                pass
        except:
            error= traceback.format_exc()
            print(f"There was an error parsing mqtt \n{error}")

    def draw_map(self, event=None):
        for i in self.checkboxes:
            i.uncheck()
        self.checkboxes[event].check()
        self.taget_sensor=self.database.sensors[event]
"""
    'conductivity': msg.conductivity,
    'temperature_ct': msg.temperature_ct,
    'turbidity': msg.turbidity,
    'ph': msg.ph,
    'vbat': msg.vbat,
    'lat': msg.lat,
    'lon': msg.lon,
    'date': msg.date,
    'veh_num': self.vehicle_id
"""

#for measures
"""
37.4185, -6.001
"""