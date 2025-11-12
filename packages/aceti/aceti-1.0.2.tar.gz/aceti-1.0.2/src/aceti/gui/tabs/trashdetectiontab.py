import tkinter
import tkinter.font
import tkinter.ttk
import os, sys
from tkintermapview import TkinterMapView
from datetime import datetime, date
import pandas as pd
import tkinter
sys.path.append('../')
from ..submodules.database import Database
from ..shared import *
from ..assets import *
from ..widgets.highlable_calendar import *
from ..widgets.labels import *
from ..widgets.map_markers import *
from ..widgets.checkbox import *
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)

class TRASHTAB(tkinter.PanedWindow):
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

        super().__init__(orient="horizontal")

        self.database= Database()
        self.date=date.today()
        self.download_loop_object = None
        self.refreshed = False
        self.busy=False
        self.sm_state=0
        self.path_map=None
        self.path_db = pd.DataFrame()
        self.trash_db = pd.DataFrame()
        self.wqp_db = pd.DataFrame()


        self.trash_tab()

    def trash_tab(self):
        self.GPS_panel = tkinter.PanedWindow(orient="vertical")
        self.add(self.GPS_panel)
        
        #create map
        self.map_widget = TkinterMapView(corner_radius=0, height=int(self.parent.screenheight*0.75)+1,database_path=self.assets.map_tiles) #this widget has no automatic size
        self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        self.GPS_panel.add(self.map_widget)
        self.topleft=[37.420088,-6.001346]
        self.bottomright=[37.418399,-5.997504]
        self.map_widget.fit_bounding_box(self.topleft, self.bottomright)


        self.trashes=[]
        self.ships=[]

        ##create info bar
        gps_data= tkinter.PanedWindow(orient="horizontal",height=1)
        self.GPS_panel.add(gps_data, minsize=60)
        #scale
        self.timeline = tkinter.Scale(gps_data, from_=0, to=0, orient="horizontal",command=self.go_to_time, bg="white")
        gps_data.add(self.timeline,width=5000)
        self.play_callback=None
        #play and center buttons
        aux=tkinter.Frame(gps_data, height=1, borderwidth=1, bg="white") 
        buttonsframe=tkinter.Frame(aux, height=1, borderwidth=1) #for date and play/center
        buttonsframe.pack(side="top")
        self.playbuttom = tkinter.Button(buttonsframe, image=self.assets.icon_play, command=self.play, width=35, height=35, bg="white")
        self.playbuttom.pack(side="left")
        self.play_status=False
        self.playbuttom["state"] = "disabled"
        self.center_buttom = tkinter.Button(buttonsframe, text="Center", command=self.center_map, width=10, height=1, bg="white")
        self.center_buttom.pack(side="right",expand="true",fill="both")
        self.speed_buttom = tkinter.Label(buttonsframe, text="x1", relief="raised" , width=5, height=1, bg="white")
        self.speed_buttom.bind("<Button-1>", self.increase_speed)
        self.speed_buttom.bind("<Button-3>", self.decrease_speed)
        self.speed=1
        self.speed_buttom.pack(side="right",expand="true",fill="y")


        #colorbar scale plot
        self.colorbar_fig, self.colorbar_ax = plt.subplots(figsize=(1,20), layout='constrained')
        self.colorbar = FigureCanvasTkAgg(self.colorbar_fig, master=self)
        self.add(self.colorbar.get_tk_widget(), minsize=30)
        
        #date
        self.date_var=tkinter.StringVar()
        self.date_label=tkinter.Label(aux, textvariable=self.date_var, width=int(self.parent.screenwidth*0.08), height=1, font=tkinter.font.Font(weight='bold', size=12))
        self.date_label.pack(side="bottom", padx=0, pady=2,anchor="c")
        
        gps_data.add(aux,minsize=200)
        
        #map selection
        self.map_selection=tkinter.Frame(self)
        self.map_selection.pack_propagate(False)
        self.add(self.map_selection, minsize=240)

        #calendar
        self.playback_selector_frame=tkinter.Frame(self.map_selection)
        self.cal = highlable_calendar(self.playback_selector_frame, selectmode = 'day', parent=self)
        self.cal.selection_set(self.date)
        self.bind("<<UpdatePlotData>>", self.download_database)

        self.cal.pack(expand="false",fill="none")
        self.refresh_buttom = tkinter.Button(self.playback_selector_frame, text="refresh", command=self.refresh_database, width=8, height=1,font=tkinter.font.Font(weight='bold', size=18))
        self.refresh_buttom.pack(side="top",expand="false",fill="x")


        self.playback_selector_frame.pack()

        self.checkboxes=[]
        for i in range(len(self.database.sensors)): #for as many sensors
            aux= Checkbox(self.map_selection, text=self.database.sensors[i], width=20, command=lambda a=i: self.draw_map(a))
            aux.pack(side="top")
            self.checkboxes.append(aux)
            aux["state"] = "disabled"
        
        self.data_points_label=tkinter.StringVar()
        a= tkinter.Frame(self.map_selection, padx=10, pady=2)
        a.pack(side='top', fill='both', expand=True,)
        a.pack_propagate(False)
        tkinter.Label(a, text="Mission Length: ", font=tkinter.font.Font(weight='bold')).pack(side="left", fill='both', padx=0, pady=2)
        tkinter.Label(a, textvariable=self.data_points_label).pack(side="left", fill='both', padx=0, pady=2)

        self.wqp_points_label=tkinter.StringVar()
        a= tkinter.Frame(self.map_selection, padx=10, pady=2)
        a.pack(side='top', fill='both', expand=True,)
        a.pack_propagate(False)
        tkinter.Label(a, text="wqp points: ", font=tkinter.font.Font(weight='bold')).pack(side="left", fill='both', padx=0, pady=2)
        tkinter.Label(a, textvariable=self.wqp_points_label).pack(side="left", fill='both', padx=0, pady=2)


        self.trash_points_label=tkinter.StringVar()
        a= tkinter.Frame(self.map_selection, padx=10, pady=2)
        a.pack(side='top', fill='both', expand=True,)
        a.pack_propagate(False)
        tkinter.Label(a, text="Trash Pressence: ", font=tkinter.font.Font(weight='bold')).pack(side="left", fill='both', padx=0, pady=2)
        tkinter.Label(a, textvariable=self.trash_points_label).pack(side="left", fill='both', padx=0, pady=2)

        self.status_label=tkinter.StringVar()
        a= tkinter.Frame(self.map_selection, padx=10, pady=2)
        a.pack(side='top', fill='both', expand=True,)
        a.pack_propagate(False)
        tkinter.Label(a, text="Status", font=tkinter.font.Font(weight='bold')).pack(side="left", fill='both', padx=0, pady=2)
        tkinter.Label(a, textvariable=self.status_label).pack(side="left", fill='both', padx=0, pady=2)
        self.status_label.set("Off")


    def play(self):
        if self.play_status:
            self.playbuttom.config(image=self.assets.icon_play)
            self.parent.after_cancel(self.play_callback)
            self.play_status=False
            self.status_label.set("Paused")
        else:
            if self.timeline.get() == len(self.path_db):
                self.timeline.set(0)
            self.playbuttom.config(image=self.assets.icon_pause)
            self.play_callback=self.parent.after(200//self.speed,self.execute_time)
            self.play_status=True
            self.status_label.set("Playing")



    def go_to_time(self, value):
        value=int(value)
        if value>=len(self.path_db):
            return
        if value == 0: #reset
            self.map_widget.delete_all_marker()
            self.map_widget.delete_all_path()
            self.ships=[]
            self.trashes=[]
            if len(self.wqp_db) >0:
                self.path_map.show_up_to(0)

        #get next time
        timestep=self.path_db.index.values[value]
        self.date_var.set(pd.to_datetime(timestep).strftime("%Y-%m-%d %H:%M:%S"))
        if len(self.wqp_db) >0:
            self.path_map.show_up_to(timestep)
        if len(self.ships)==0:
            self.ships =[SHIP("ASV1", self.path_db.at[timestep,"Latitude"], self.path_db.at[timestep,"Longitude"], rotation=-self.path_db.at[timestep,"Heading"], parent=self)]
        else:
            self.ships[0].update_rotation(-self.path_db.at[timestep,"Heading"])
            self.ships[0].set_position(self.path_db.at[timestep,"Latitude"], self.path_db.at[timestep,"Longitude"])
        if timestep in self.trash_db.index.values:
            if len(self.trashes)==0:
                self.trashes=[TRASH("Trash_1", self.trash_db.at[timestep,"Latitude_Obj"],self.trash_db.at[timestep,"Longitude_Obj"], parent=self)]
            else:
                self.trashes[0].update_position(self.trash_db.at[timestep,"Latitude_Obj"],self.trash_db.at[timestep,"Longitude_Obj"])
        else:
            if len(self.trashes)!=0:
                self.trashes[0].hide_image(True)

            
    def execute_time(self):
        if self.timeline.get() == len(self.path_db) and self.play_status:
            self.play() #stop time
            return
        self.timeline.set(self.timeline.get()+1)
        self.play_callback=self.parent.after(200//self.speed,self.execute_time)
        
    def increase_speed(self, event=None):
        if self.speed<8:
            self.speed+=1
        self.speed_buttom.config(text=f"x{self.speed}")

    def decrease_speed(self, event=None):
        if self.speed>1:
            self.speed-=1
        self.speed_buttom.config(text=f"x{self.speed}")


    def center_map(self,event=None):
        self.map_widget.fit_bounding_box(self.topleft, self.bottomright)


    def refresh_database(self, event=None):
        self.database.refresh_dates(table="PATHS")
        self.cal.unhighlight()
        for _date in self.database.date_df:
            dat=date.fromisoformat(_date)
            self.cal.add_to_data(dat)
        self.refreshed = True

    def download_database(self, event=None):
        if self.play_status:
            self.play()
        if self.sm_state == 0: #Query Path
            if not self.busy:
                self.timeline.config(to=0)
                self.playbuttom["state"] = "disabled"
                self.date=self.cal.selection_get()
                self.date_var.set(self.date.isoformat())
                self.status_label.set("Querying Database")
                date_=self.date.strftime("%Y-%m-%d")
                query=f"SELECT Date,Latitude,Longitude,Heading,ASV FROM wqp.PATHS where date(Date) = '{date_}' AND Latitude<>0;"
                self.database.query(query=query)
                self.busy=True
            else:
                if not self.database.busy:
                    self.busy=False
                    self.path_db=self.database.df
                    self.sm_state=1
            self.download_loop_object = self.parent.after(20,self.download_database)

        if self.sm_state == 1: #Query Path
            if not self.busy:
                self.status_label.set("Querying WQP Database")
                date_=self.date.strftime("%Y-%m-%d")
                query=f"SELECT Date,Latitude,Longitude,Sensor,Data FROM wqp.WQP where date(Date) = '{date_}' AND Latitude<>0;"
                self.database.query(query=query)
                self.busy=True
            else:
                if not self.database.busy:
                    self.busy=False
                    self.wqp_db=self.database.df
                    self.sm_state=2
            self.download_loop_object = self.parent.after(20,self.download_database)

        elif self.sm_state == 2: #query trash
            if not self.busy:
                self.status_label.set("Querying Trash locations")
                date_=self.date.strftime("%Y-%m-%d")
                query=f"SELECT Date, Latitude_Obj, Longitude_Obj, ASV FROM wqp.OBJECT_POSITION where date(Date) = '{date_}' AND Latitude_Obj<>0;"
                self.database.query(query=query)
                self.busy=True
                self.download_loop_object = self.parent.after(20,self.download_database)

            else:
                if self.database.busy:
                    self.download_loop_object = self.parent.after(20,self.download_database)
                else:
                    #load database
                    self.trash_db=self.database.df
                    self.busy=False
                    self.sm_state=0
                    self.parent.after_cancel(self.download_loop_object)
                    self.load_database()


    def load_database(self):
        self.status_label.set("Processing Data")

        #take mean and only 1sec per data
        self.path_db = self.path_db.groupby(["Date"]).mean()
        if len(self.path_db) >3600:
            duration= "{:02d}".format(len(self.path_db)//3600) + ":" +"{:02d}".format((len(self.path_db)%3600)//60) + ":" + "{:02d}".format(len(self.path_db)%60)
        else:
            duration= "{:02d}".format((len(self.path_db)%3600)//60) + ":" + "{:02d}".format(len(self.path_db)%60)
        self.data_points_label.set(duration)
        if len(self.wqp_db) > 0:
            self.wqp_db = self.wqp_db.groupby(["Date","Sensor"]).mean().reset_index()
            self.wqp_db = self.wqp_db.set_index(["Date"])
            self.wqp_db = self.wqp_db[self.wqp_db["Data"]!=0]
        self.wqp_points_label.set(len(self.wqp_db))
        if len(self.trash_db) >0:
            self.trash_db = self.trash_db.groupby(["Date"]).mean()
        self.trash_points_label.set(len(self.trash_db))

        self.timeline.config(to=len(self.path_db))
        self.path_map = PATH(self.wqp_db, parent =self)
        for check in self.checkboxes:
            check["state"] = "normal"
        self.draw_map(0)
        self.go_to_time(0)
        self.playbuttom["state"] = "normal"
        self.status_label.set("Paused")



            
    def draw_map(self, event=None):
        for i in self.checkboxes:
            i.uncheck()
        self.checkboxes[event].check()
        if self.path_map is not None:
            self.path_map.select_sensor(self.database.sensors[event])


    def close(self):
        # stop play loop if running
        try:
            if self.play_status:
                self.play()
        except Exception:
            pass
        # cancel any pending download loop
        try:
            if hasattr(self, 'download_loop_object') and self.download_loop_object:
                self.parent.after_cancel(self.download_loop_object)
                self.download_loop_object = None
        except Exception:
            pass
        # attempt to destroy map widget and its markers to prevent callbacks after destruction
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
