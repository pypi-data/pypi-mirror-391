import tkinter
import tkinter.font
import tkinter.ttk
import os, sys
from tkintermapview.canvas_position_marker import CanvasPositionMarker
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime, date
sys.path.append('../')
from ..shared import *
from ..assets import *
from ..widgets.labels import *
from ..submodules.database import Database
from ..widgets.highlable_calendar import *
from ..widgets.checkbox import *


class GAUSIANSENSORTAB(tkinter.PanedWindow):
    def __init__(self, parent=None):
        if parent is None:
            parent=tkinter.Tk()
        self.parent=parent
        self.busy=False
        self.checkboxes=[]
        self.gp_loop_object = None
        self.date=date.today()
        self.date_var = tkinter.StringVar()
        self.refreshed=False

        #inherit
        try:
            self.assets=self.parent.assets
            self.shared=self.parent.shared
        except:
            self.assets=Assets()
            self.shared=SHARED()

        super().__init__(orient="horizontal")
        self.database= Database()
        self.taget_sensor=self.database.sensors[0]
        self.gp_step=0
        self.gs_tab()

    def gs_tab(self):
        self.GPS_panel = tkinter.PanedWindow(orient="vertical", width=int(self.parent.screenwidth*0.8))
        self.add(self.GPS_panel)

        #create map
        self.fig, self.axis = plt.subplots()
        self.map_widget = FigureCanvasTkAgg(self.fig, master=self.GPS_panel)  # A tk.DrawingArea.
        self.GPS_panel.add(self.map_widget.get_tk_widget(), stretch="always")
        # self.map_widget.pack_propagate(False)

        #map selection
        self.map_selection=tkinter.Frame(self, width=20)
        self.map_selection.pack_propagate(False)
        self.add(self.map_selection, minsize=200)
        for i in range(len(self.database.sensors)): #for as many sensors
            aux= Checkbox(self.map_selection, text=self.database.sensors[i], width=20, command=lambda a=i: self.draw_map(a))
            aux.pack(side="top")
            self.checkboxes.append(aux)
        self.checkboxes[0].check()

        #calendar
        self.playback_selector_frame=tkinter.Frame(self.map_selection)
        #day=datetime.now()
        self.cal = highlable_calendar(self.playback_selector_frame, selectmode = 'day', parent=self)
        self.cal.selection_set(self.date)
        self.bind("<<UpdatePlotData>>", self.download_database)
        self.cal.pack( expand="false",fill="none")
        self.refresh_buttom = tkinter.Button(self.playback_selector_frame, text="refresh", command=self.refresh_database, width=8, height=1,font=tkinter.font.Font(weight='bold', size=18))
        self.refresh_buttom.pack(side="top",expand="false",fill="x")


        self.map_selection_frame=tkinter.Frame(self.map_selection)

        tkinter.Label(self.map_selection_frame, text="Map Selector", font=tkinter.font.Font(weight='bold')).pack(side="top", fill='x', padx=0, pady=2)

        self.map_selector = tkinter.ttk.Combobox(self.map_selection_frame, values=["Alamillo", "Alamillo30x49", "AlamilloAccess11x15"], state="readonly")
        self.map_selector.pack(side="top",expand="false",fill="x", pady=10)

        self.playback_selector_frame.pack()
        self.map_selection_frame.pack()
        
        self.status_label=tkinter.StringVar()
        a= tkinter.Frame(self.map_selection, padx=10, pady=2)
        a.pack(side='top', fill='both', expand=True,)
        a.pack_propagate(False)
        tkinter.Label(a, text="Status", font=tkinter.font.Font(weight='bold')).pack(side="left", fill='both', padx=0, pady=2)
        tkinter.Label(a, textvariable=self.status_label).pack(side="left", fill='both', padx=0, pady=2)
        self.status_label.set("Off")

    def refresh_database(self, event=None):
        self.database.refresh_dates(database="alec", table="wqp_gaussian_maps")
        self.cal.unhighlight()
        for _date in self.database.date_df:
            dat=date.fromisoformat(_date)
            self.cal.add_to_data(dat)
        self.refreshed=True

        
    def draw_map(self, event=None):
        for i in self.checkboxes:
            i.uncheck()
        self.checkboxes[event].check()
        self.taget_sensor=self.database.sensors[event]
        self.download_database()


    def download_database(self, event=None):
        if not self.busy:
            self.date=self.cal.selection_get()
            self.date_var.set(self.date.isoformat())
            self.status_label.set("Querying Database")
            date_=self.date.strftime("%Y-%m-%d")
            print(self.map_selector["values"][self.map_selector.current()])
            query=f"SELECT * FROM alec.wqp_gaussian_maps where date(Date) = '{date_}' and Sensor = '{self.taget_sensor}' and mapa = '{self.map_selector['values'    ][self.map_selector.current()]}';"
            self.database.query(query=query, database="alec")
            self.busy=True
        else:
            if not self.database.busy:
                self.busy=False
                self.df=self.database.df
                self.create_map()
                return
        self.download_loop_object = self.parent.after(20,self.download_database)




    def close(self):
        # cancel any scheduled download loop
        try:
            if hasattr(self, 'download_loop_object') and self.download_loop_object:
                self.parent.after_cancel(self.download_loop_object)
                self.download_loop_object = None
        except Exception:
            pass
        # attempt to destroy the matplotlib canvas to stop internal callbacks
        try:
            if hasattr(self, 'map_widget') and self.map_widget is not None:
                try:
                    widget = self.map_widget.get_tk_widget()
                    widget.destroy()
                except Exception:
                    pass
                try:
                    self.map_widget = None
                except Exception:
                    pass
        except Exception:
            pass

    def open(self):
        if self.refreshed==False:
            self.refresh_database()
            maps=self.database.refresh_maps()
            print(maps)
            self.map_selector.config(values=list(maps))
            self.map_selector.set(maps[0])


    def create_map(self):
        if len(self.df)>0:
            self.status_label.set("Drawing map")
        else:
            self.status_label.set("No map to draw")
        x=self.df["x"]
        y=self.df["y"]

        mean_map=[]
        for row in self.df["mean_map"].values:
            try:
                mean_map.append(row[1:-1].replace(" ","").split(","))
            except:
                pass
        mean_map=np.asarray(mean_map).astype(float)
        self.fig.clf()
        self.axis = self.fig.add_subplot(111)
        self.axis.set_xticks([])
        self.axis.set_yticks([])

        # Ajusta los márgenes del subplot para ocupar todo el espacio
        self.fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
        self.axis.set_position([0, 0, 1, 1])

        # Contorno
        # cs_internos = plt.contour(mean_map, colors='black', alpha=0.7, linewidths=0.7, zorder=1)
        # cs_externo = plt.contour(mean_map, colors='black', alpha=1, linewidths=1.7, zorder=1)

        # cs_internos.collections[0].remove()
        # for i in range(1, len(cs_externo.collections)):
        #     cs_externo.collections[i].remove()
        # plt.clabel(cs_internos, inline=1, fontsize=3.5)

        # Mapa y puntos de muestreo
        self.axis.scatter(x, y, c='black', s=1, marker='.', alpha=0.5)
        vmin = np.min(mean_map[mean_map > 0])
        vmax = np.max(mean_map[mean_map > 0])
        im= self.axis.imshow(mean_map, cmap='viridis', alpha=1, origin='upper', vmin=vmin, vmax=vmax)

        # Recortar el mapa
        # plt.ylim(1150, 200)

        # Leyendas
        # unidades_dict = {'Sonar': 'Profundidad (m)', 'Conductivity': 'Conductividad (mS/cm)', 'PH': 'pH', 'Temperature': 'Temperatura (ºC)', 'Turbidity': 'Turbidez (NTU)'}
        # nombre_dict = {'Sonar': 'Batimetría', 'Conductivity': 'Conductividad', 'PH': 'pH', 'Temperature': 'Temperatura', 'Turbidity': 'Turbidez'}
        unidades_dict = {'Sonar': 'Deepness (m)', 'Conductivity': 'Conductivity (mS/cm)', 'PH': 'pH', 'Temperature': 'Temperature (ºC)', 'Turbidity': 'Turbidity (NTU)'}
        nombre_dict = {'Sonar': 'Bathymetry', 'Conductivity': 'Conductivity', 'PH': 'pH', 'Temperature': 'Temperature', 'Turbidity': 'Turbidity'}
        cbar = self.fig.colorbar(im, shrink=0.65, ax=self.axis)
        cbar.set_label(label=unidades_dict[self.taget_sensor],size=12)#,weight='bold')
        # plt.title(f'{nombre_dict[self.taget_sensor]} del Lago Mayor (Parque del Alamillo)')
        self.axis.set_title(f'{nombre_dict[self.taget_sensor]} Major Lake (Alamillo)')
        # self.fig.savefig("mapa.pdf", bbox_inches='tight')
        self.map_widget.draw()
        self.status_label.set("Iddle")
