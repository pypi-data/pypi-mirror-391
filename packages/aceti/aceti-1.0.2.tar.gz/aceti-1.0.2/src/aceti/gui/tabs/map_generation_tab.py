import tkinter
import tkinter.font
import tkinter.ttk
import os, sys, webbrowser, platform
import signal
import random
from tkintermapview import TkinterMapView
from tkintermapview.canvas_position_marker import CanvasPositionMarker
import threading
import time
import screeninfo
import traceback
import re
import requests
import math
import pandas as pd
from PIL import Image, ImageTk
sys.path.append('../')
from ..shared import *
from ..assets import *
from ..widgets.ListboxEditable import ListboxEditable
from ..widgets.labels import *
from .map_creation_window import MapCreationWindow
max_retain_data=40


class MAP_GENERATOR_WIDGET(TkinterMapView):
    def __init__(self, *args, parent=None, **kwargs):
        self.assets=parent.assets
        self.parent=parent
        super().__init__(*args,**kwargs)


class MAP_GENERATORTAB(tkinter.ttk.PanedWindow):
    def __init__(self, parent=None):
        if parent is None:
            parent=tkinter.Tk()
        self.parent=parent
        self.polygon=None
        #inherit
        try:
            self.assets=self.parent.assets
            self.shared=self.parent.shared
        except:
            self.assets=Assets()
            self.shared=SHARED()

        super().__init__(orient="horizontal")
        self.gs_tab()

    def gs_tab(self):
        self.GPS_panel = tkinter.ttk.PanedWindow(orient="vertical")
        self.add(self.GPS_panel)

        #create map
        self.map_widget = MAP_GENERATOR_WIDGET(parent= self,corner_radius=0,width=int(self.parent.screenwidth*0.75)+1, height=int(self.parent.screenheight*0.75)+1) #this widget has no automatic size
        self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        self.GPS_panel.add(self.map_widget)
        # self.map_widget.pack_propagate(False)
        self.topleft=[37.420088,-6.001346]
        self.bottomright=[37.418399,-5.997504]
        self.map_widget.fit_bounding_box(self.topleft, self.bottomright)

        #map selection
        self.map_selection=tkinter.Frame(self, width=20)
        self.map_selection.pack_propagate(False)
        self.add(self.map_selection)

        self.map_selection_frame=tkinter.Frame(self.map_selection)
        self.map_selection_frame.pack(side="top", fill="x")
        #Label barra de búsqueda
        self.map_search_label=tkinter.Label(self.map_selection_frame, text="1 Barra de Búsqueda",font=tkinter.font.Font(weight='bold', size=18))
        self.map_search_label.pack(side="top",pady=15)
        # search bar for tkintermapview
        self.search_frame = tkinter.Frame(self.map_selection_frame)
        self.search_entry = tkinter.Entry(self.search_frame)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0,4))
        self.search_button = tkinter.Button(self.search_frame, image=self.assets.icon_lupa, command=self.search_location, width=36, height=36)
        self.search_button.pack(side="right")
        self.search_entry.bind("<Return>", self.search_location)
        self.search_frame.pack(side="top", fill="x", pady=(10,5))

        #L selecciona las esquinas del mapa
        self.map_search_label=tkinter.Label(self.map_selection_frame, text="2 Corner selector",font=tkinter.font.Font(weight='bold', size=18))
        self.map_search_label.pack(side="top",pady=15)


        # 2 botones para elegir puntos de coordenadas de dos esquinas cuando pulse en el mapa despues de estos
        self.northwest_selection_frame=tkinter.Frame(self.map_selection)
        self.northwest_selection_frame.pack(side="top", fill="x", pady=(10,5))
        self.map_selection_button1 = tkinter.Button(self.northwest_selection_frame, text="Esquina 1", command=self.select_top_left)
        self.map_selection_button1.pack(side="left", pady=5)
        # use StringVar so we can trace changes
        self.northwest_var_lat = tkinter.StringVar()
        self.northwest_var_lon = tkinter.StringVar()
        self.northwest_entry_lat = tkinter.Entry(self.northwest_selection_frame, textvariable=self.northwest_var_lat)
        self.northwest_entry_lat.pack(side="left", fill="x", expand=True, padx=(0,4))
        self.northwest_entry_lon = tkinter.Entry(self.northwest_selection_frame, textvariable=self.northwest_var_lon)
        self.northwest_entry_lon.pack(side="left", fill="x", expand=True, padx=(0,4))

        self.southeast_selection_frame=tkinter.Frame(self.map_selection)
        self.southeast_selection_frame.pack(side="top", fill="x", pady=(10,5))
        self.map_selection_button2 = tkinter.Button(self.southeast_selection_frame, text="Esquina 2", command=self.select_bottom_right)
        self.map_selection_button2.pack(side="left", pady=5)
        # use StringVar so we can trace changes
        self.southeast_var_lat = tkinter.StringVar()
        self.southeast_var_lon = tkinter.StringVar()
        self.southeast_entry_lat = tkinter.Entry(self.southeast_selection_frame, textvariable=self.southeast_var_lat)
        self.southeast_entry_lat.pack(side="left", fill="x", expand=True, padx=(0,4))
        self.southeast_entry_lon = tkinter.Entry(self.southeast_selection_frame, textvariable=self.southeast_var_lon)
        self.southeast_entry_lon.pack(side="left", fill="x", expand=True, padx=(0,4))

        # add traces so any change to these variables updates the polygon
        try:
            for var in (self.northwest_var_lat, self.northwest_var_lon, self.southeast_var_lat, self.southeast_var_lon):
                # trace_add is preferred in modern tkinter
                try:
                    var.trace_add('write', self.writepolygon)
                except Exception:
                    # fallback to older trace
                    var.trace('w', lambda *args, v=var: self.writepolygon())
        except Exception:
            pass


        #L selecciona las esquinas del mapa
        self.map_config_label=tkinter.Label(self.map_selection_frame, text="3 Configuracion",font=tkinter.font.Font(weight='bold', size=18))
        self.map_config_label.pack(side="top",pady=15)

        # Configuración de la selección del mapa
        self.map_config_frame = tkinter.Frame(self.map_selection_frame)
        self.map_config_frame.pack(side="top", fill="x", pady=(10, 5))

        tkinter.Label(self.map_config_frame, text="Grid Size (meters):").pack(side="left", padx=(0, 10))

        self.gridsize_var = tkinter.StringVar()
        self.gridsize_var.set("1.0")
        vcmd = (self.register(self._validate_float), '%P')
        self.grid_check = tkinter.Entry(self.map_config_frame, textvariable=self.gridsize_var)
        self.grid_check.pack(side="left", padx=(0, 10))
        self.grid_check.config(validate='key', validatecommand=vcmd)
        self.gridsize_var.trace_add('write', lambda *args: print(f"Grid size set to: {self.gridsize_var.get()}"))


        #botón de continuar
        self.map_selection_button = tkinter.Button(self.map_selection_frame, text="Continue", command = self.to_map_creator)
        self.map_selection_button.pack(side="top", pady = 50)

    def select_top_left(self):
        def callback(event):
            try:
                lat, lon = self.map_widget.convert_canvas_coords_to_decimal_coords(event.x, event.y)
            except Exception:
                # fallback: use event coordinates if conversion not available
                try:
                    lat, lon = event.lat, event.lon
                except Exception:
                    print("Could not get coordinates from click event")
                    return
            # write coordinates to entries
            try:
                # update traced variables (these will trigger writepolygon)
                try:
                    self.northwest_var_lat.set(f"{lat:.6f}")
                    self.northwest_var_lon.set(f"{lon:.6f}")
                except Exception:
                    # fallback: write directly to entries
                    self.northwest_entry_lat.delete(0, 'end')
                    self.northwest_entry_lat.insert(0, f"{lat:.6f}")
                    self.northwest_entry_lon.delete(0, 'end')
                    self.northwest_entry_lon.insert(0, f"{lon:.6f}")
            except Exception:
                pass
            # unbind the click handler
            try:
                self.map_widget.canvas.unbind("<Button-1>")
                self.map_widget.canvas.bind("<Button-1>", self.map_widget.mouse_click)

            except Exception:
                pass
        self.map_widget.canvas.unbind("<Button-1>")
        self.map_widget.canvas.bind("<Button-1>", callback)

    def _validate_float(self, proposed):
        """Return True if proposed string is empty or a float with up to 2 decimals."""
        if proposed == "":
            return True
        try:
            # allow a leading minus and decimals
            # but enforce at most 2 decimals while typing
            m = re.match(r'^-?\d*(?:\.(\d{0,2})?)?$', proposed)
            return m is not None
        except Exception:
            return False

    def select_bottom_right(self):
        def callback(event):
            try:
                lat, lon = self.map_widget.convert_canvas_coords_to_decimal_coords(event.x, event.y)
            except Exception:
                try:
                    lat, lon = event.lat, event.lon
                except Exception:
                    print("Could not get coordinates from click event")
                    return
            try:
                # update traced variables (these will trigger writepolygon)
                try:
                    self.southeast_var_lat.set(f"{lat:.6f}")
                    self.southeast_var_lon.set(f"{lon:.6f}")
                except Exception:
                    self.southeast_entry_lat.delete(0, 'end')
                    self.southeast_entry_lat.insert(0, f"{lat:.6f}")
                    self.southeast_entry_lon.delete(0, 'end')
                    self.southeast_entry_lon.insert(0, f"{lon:.6f}")
            except Exception:
                pass
            try:
                self.map_widget.canvas.unbind("<Button-1>")
                self.map_widget.canvas.bind("<Button-1>", self.map_widget.mouse_click)
            except Exception:
                pass
            print(f"Bottom-right corner set to: {self.southeast_entry_lat.get()}, {self.southeast_entry_lon.get()}")

        self.map_widget.canvas.unbind("<Button-1>")
        self.map_widget.canvas.bind("<Button-1>", callback)

    def search_location(self, event=None):
        try:
            query = self.search_entry.get().strip()
            if not query:
                return
            # simple rate-limit to avoid rapid repeated queries
            try:
                import time
                now = time.time()
                if getattr(self, '_last_search', 0) and now - self._last_search < 1.0:
                    # ignore searches less than 1s apart
                    return
                self._last_search = now
            except Exception:
                pass

            # First, try a direct Nominatim HTTP request with proper identification
            try:
                nominatim_url = "https://nominatim.openstreetmap.org/search"
                headers = {"User-Agent": "aceti_maps/0.0.2 (acasado4@us.es)"}
                params = {"q": query, "format": "jsonv2", "addressdetails": 1, "limit": 1, "email": "acasado4@us.es"}
                resp = requests.get(nominatim_url, params=params, headers=headers, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    if data:
                        lat = float(data[0]["lat"])
                        lon = float(data[0]["lon"])
                        try:
                            self.map_widget.set_position(lat, lon)
                            self.map_widget.set_zoom(19)
                            return
                        except Exception:
                            pass
                    else:
                        print(f"No geocoding results for '{query}'")
                else:
                    # Nominatim may return 403 if our requests are blocked/rate-limited
                    print(f"Nominatim HTTP error {resp.status_code} for query '{query}'")
                    if resp.status_code == 403:
                        print("Nominatim returned 403 — you may be rate-limited or blocked. Consider using an API key provider or running a local Nominatim instance.")
            except Exception as e:
                print(f"Direct Nominatim request failed: {e}")

            # Fallback to internal geocoder provided by tkintermapview (may hit same service)
            try:
                self.map_widget.set_address(query)
                return
            except Exception:
                # if that fails, try interpreting the query as 'lat, lon'
                m = re.match(r"\s*([+-]?\d+\.?\d*)[,\s]+([+-]?\d+\.?\d*)\s*$", query)
                if m:
                    lat = float(m.group(1))
                    lon = float(m.group(2))
                    try:
                        self.map_widget.set_position(lat, lon)
                        self.map_widget.set_zoom(15)
                        return
                    except Exception:
                        pass
                print(f"Search failed for '{query}' (no geocoding result)")
        except Exception as e:
            print(f"Error in search_location: {e}")


    def writepolygon(self, *args):
        """Draw or update a rectangular polygon from northwest and southeast variables."""
        try:
            lat1 = float(self.northwest_var_lat.get())
            lon1 = float(self.northwest_var_lon.get())
            lat2 = float(self.southeast_var_lat.get())
            lon2 = float(self.southeast_var_lon.get())
        except Exception:
            return

        # ensure lat1 is the northern (greater) and lat2 is southern (smaller) if user inverted
        try:
            if lat2 > lat1:
                lat1, lat2 = lat2, lat1
            if lon1 > lon2:
                lon1, lon2 = lon2, lon1
        except Exception:
            pass

        coords = [(lat1, lon1), (lat1, lon2), (lat2, lon2), (lat2, lon1), (lat1, lon1)]

        try:
            # remove previous polygon/path if exists
            try:
                if getattr(self, 'polygon', None):
                    try:
                        # some objects may provide a delete method
                        if hasattr(self.polygon, 'delete'):
                            self.polygon.delete()
                        elif hasattr(self.polygon, 'remove'):
                            self.polygon.remove()
                    except Exception:
                        pass
                    self.polygon = None
            except Exception:
                pass

            # try set_polygon (if available), otherwise use set_path
            try:
                self.polygon = self.map_widget.set_polygon(coords)
            except Exception:
                try:
                    # delete all paths to avoid duplicates
                    try:
                        self.map_widget.delete_all_path()
                    except Exception:
                        pass
                    self.polygon = self.map_widget.set_path(coords)
                except Exception as e:
                    print(f"Could not draw polygon: {e}")
        except Exception as e:
            print(f"writepolygon error: {e}")

    def center_map(self,event=None):
        self.map_widget.fit_bounding_box(self.topleft, self.bottomright)

    def to_map_creator(self, event=None):

        try:
            lat1 = float(self.northwest_var_lat.get())
            lon1 = float(self.northwest_var_lon.get())
            lat2 = float(self.southeast_var_lat.get())
            lon2 = float(self.southeast_var_lon.get())
            if lat2 > lat1:
                lat1, lat2 = lat2, lat1
            if lon1 > lon2:
                lon1, lon2 = lon2, lon1
            #if they look like numbers
            if not all(isinstance(coord, float) for coord in (lat1, lon1, lat2, lon2)):
                raise ValueError("Coordinates must be numeric.")
        except Exception as e:
            tkinter.messagebox.showerror("Invalid Coordinates", "Please enter valid numeric coordinates for both corners.")
            return
        try:
            MapCreationWindow(self, northwest=[lat1, lon1], southeast=[lat2, lon2], gridsize=float(self.gridsize_var.get()))
        except Exception as e:
            print(f"Error in to_map_creator: {e}")

    

    def close(self):
        pass

    def open(self):
        pass
