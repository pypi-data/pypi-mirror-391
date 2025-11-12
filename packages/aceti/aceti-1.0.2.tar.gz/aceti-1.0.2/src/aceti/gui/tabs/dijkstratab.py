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
from ..widgets.labels import *
from ..widgets.highlable_calendar import *
from ..widgets.map_markers import *
from ..widgets.checkbox import *
from ..submodules.dijkstra import Dijkstra, reduce_path, reduce_path_bresenham, reduce_path_douglas_peucker, reduce_path_new



class DIJKSTRATAB(tkinter.ttk.PanedWindow):
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
        
        self.date=date.today()
        self.on_status=True
        self.waiting=False
        
        super().__init__(orient="horizontal")

        self.dijkstra_tab()
        # self.playback_data()
        # mapa = 'assets/Maps/alamillo.npy'
        mapa = self.parent.assets.resource_path('assets/Maps/Alamillo95x216plantilla.csv')
        # Robust map loader: try numpy with comma, then whitespace, then pandas as fallback
        if mapa.endswith('.npy'):
            self.map = np.load(mapa)
        elif mapa.endswith('.csv') or mapa.endswith('.txt'):
            # try comma-delimited first
            try:
                self.map = np.loadtxt(mapa, delimiter=',')
            except Exception:
                # try whitespace-delimited
                try:
                    self.map = np.loadtxt(mapa)
                except Exception:
                    # last resort: use pandas with delim_whitespace (handles mixed separators)
                    try:
                        import pandas as pd
                        self.map = pd.read_csv(mapa, header=None, delim_whitespace=True).to_numpy()
                    except Exception:
                        # give up and keep None to avoid crashing here
                        self.map = None
        else:
            # default fallback
            try:
                self.map = np.loadtxt(mapa, delimiter=',')
            except Exception:
                try:
                    self.map = np.loadtxt(mapa)
                except Exception:
                    self.map = None
        self.obstacle_map=np.logical_not(self.map)
        self.dijkstra = Dijkstra(self.map, 1)

    def dijkstra_tab(self):
        self.Map_panel = tkinter.ttk.PanedWindow(orient="vertical", width=int(self.parent.screenwidth*0.8))
        self.add(self.Map_panel)

        
        #create map
        self.cell_map_frame = tkinter.Frame(self.Map_panel)
        self.cell_map_frame.pack_propagate(False)
        self._selected_cell = None
        self._selected_cell2 = None
        # default cell size in pixels (will be scaled if map too large)
        self._cell_size = 8
        self.cell_canvas = tkinter.Canvas(self.cell_map_frame, bg='white')
        self.cell_canvas.pack(fill='both', expand=True)
        # place the frame inside the panel
        try:
            self.Map_panel.add(self.cell_map_frame)
        except Exception:
            # fallback if add not allowed (older Tk versions)
            self.add(self.cell_map_frame)

        # bind resize to redraw
        self.cell_canvas.bind('<Configure>', lambda e: self.draw_cell_map())
        # bind click
        self.cell_canvas.bind('<Button-1>', self._on_cell_click)
        self.cell_canvas.bind('<Button-3>', self._on_cell_right_click)



        #map selection
        self.map_selection=tkinter.Frame(self, width=20)
        self.map_selection.pack_propagate(False)
        self.add(self.map_selection)

        self.checkboxes=[]
        self.algorithms=["syanes", "bressen", "douglas_peucker", "new_syanes"]
        for i in range(len(self.algorithms)): #for as many sensors
            aux= Checkbox(self.map_selection, text=self.algorithms[i], width=20, command=lambda a=i: self.draw_map(a))
            aux.pack(side="top")
            self.checkboxes.append(aux)
        self.algo = "syanes"
        self.checkboxes[0].check()


        self.origin_label=tkinter.StringVar()
        a= tkinter.Frame(self.map_selection, padx=10, pady=2)
        a.pack(side='top', fill='both', expand=True,)
        a.pack_propagate(False)
        tkinter.Label(a, text="Origin ", font=tkinter.font.Font(weight='bold')).pack(side="left", fill='both', padx=0, pady=2)
        tkinter.Label(a, textvariable=self.origin_label).pack(side="left", fill='both', padx=0, pady=2)
        self.origin_label.set("Null")

        self.final_label=tkinter.StringVar()
        a= tkinter.Frame(self.map_selection, padx=10, pady=2)
        a.pack(side='top', fill='both', expand=True,)
        a.pack_propagate(False)
        tkinter.Label(a, text="Destination ", font=tkinter.font.Font(weight='bold')).pack(side="left", fill='both', padx=0, pady=2)
        tkinter.Label(a, textvariable=self.final_label).pack(side="left", fill='both', padx=0, pady=2)
        self.origin_label.set("Null")

        self.dtime_label=tkinter.StringVar()
        a= tkinter.Frame(self.map_selection, padx=10, pady=2)
        a.pack(side='top', fill='both', expand=True,)
        a.pack_propagate(False)
        tkinter.Label(a, text="Time: ", font=tkinter.font.Font(weight='bold')).pack(side="left", fill='both', padx=0, pady=2)
        tkinter.Label(a, textvariable=self.dtime_label).pack(side="left", fill='both', padx=0, pady=2)
        self.dtime_label.set("Null")

        self.dtime2_label=tkinter.StringVar()
        a= tkinter.Frame(self.map_selection, padx=10, pady=2)
        a.pack(side='top', fill='both', expand=True,)
        a.pack_propagate(False)
        tkinter.Label(a, text="Time reduction: ", font=tkinter.font.Font(weight='bold')).pack(side="left", fill='both', padx=0, pady=2)
        tkinter.Label(a, textvariable=self.dtime2_label).pack(side="left", fill='both', padx=0, pady=2)
        self.dtime2_label.set("Null")

        self.number_of_nodes=tkinter.StringVar()
        a= tkinter.Frame(self.map_selection, padx=10, pady=2)
        a.pack(side='top', fill='both', expand=True,)
        a.pack_propagate(False)
        tkinter.Label(a, text="Number of Nodes", font=tkinter.font.Font(weight='bold')).pack(side="left", fill='both', padx=0, pady=2)
        tkinter.Label(a, textvariable=self.number_of_nodes).pack(side="left", fill='both', padx=0, pady=2)
        self.number_of_nodes.set("Null")

        self.distance_label=tkinter.StringVar()
        a= tkinter.Frame(self.map_selection, padx=10, pady=2)
        a.pack(side='top', fill='both', expand=True,)
        a.pack_propagate(False)
        tkinter.Label(a, text="Distance", font=tkinter.font.Font(weight='bold')).pack(side="left", fill='both', padx=0, pady=2)
        tkinter.Label(a, textvariable=self.distance_label).pack(side="left", fill='both', padx=0, pady=2)
        self.distance_label.set("Null")


    def close(self):
        pass

    def open(self):
        pass

    def draw_map(self, event=None):
        for i in self.checkboxes:
            i.uncheck()
        self.checkboxes[event].check()
        self.algo=self.algorithms[event]
        self.calculate_dijkstra()


    def draw_cell_map(self):
        """Render self.map (numpy 2D array) into the canvas as a grid of rectangles.

        Each cell will have a tag like "cell_r_c" to allow easy identification.
        """
        # clear
        canvas = self.cell_canvas
        canvas.delete('all')
        if not hasattr(self, 'map') or self.map is None:
            return
        try:
            arr = np.array(self.map)
        except Exception:
            return

        # If arr contains strings (e.g. each row is a long space-separated string),
        # try to parse into numeric 2D array.
        a = None
        try:
            # Fast path: numeric conversion
            a = arr.astype(float)
        except Exception:
            try:
                # handle common cases where each row is a single string with spaces
                if arr.dtype.kind in ('U', 'S', 'O'):
                    # 1D of strings
                    if arr.ndim == 1:
                        parsed = [list(map(float, str(r).strip().replace(',', ' ').split())) for r in arr]
                        a = np.array(parsed, dtype=float)
                    # 2D but single-column of strings
                    elif arr.ndim == 2 and arr.shape[1] == 1:
                        parsed = [list(map(float, str(r[0]).strip().replace(',', ' ').split())) for r in arr]
                        a = np.array(parsed, dtype=float)
                    else:
                        # try flattening and converting
                        a = np.array(arr.flatten(), dtype=float)
                else:
                    a = np.array(arr, dtype=float)
            except Exception:
                # give up if cannot parse
                return

        # Ensure 2D
        if a.ndim != 2:
            try:
                a = np.squeeze(a)
            except Exception:
                return
        if a.ndim != 2:
            return

        h, w = a.shape
        # determine cell size to fit into canvas while keeping minimum size
        canvas_w = max(canvas.winfo_width(), 50)
        canvas_h = max(canvas.winfo_height(), 50)
        cell_w = max(1, int(canvas_w / w))
        cell_h = max(1, int(canvas_h / h))
        cell_size = min(cell_w, cell_h)
        # cap cell size for performance
        cell_size = min(cell_size, max(self._cell_size, 20))

        # normalize array to 0..1 for grayscale
        amin = np.nanmin(a)
        amax = np.nanmax(a)
        if amax - amin == 0:
            norm = np.zeros_like(a)
        else:
            norm = (a - amin) / (amax - amin)

        # draw rectangles
        for r in range(h):
            y1 = r * cell_size
            y2 = y1 + cell_size
            for c in range(w):
                x1 = c * cell_size
                x2 = x1 + cell_size
                v = norm[r, c]
                gray = int((v * 255))
                color = f"#{gray:02x}{gray:02x}{gray:02x}"
                tag = f"cell_{r}_{c}"
                # draw
                canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='', tags=(tag, 'cell'))

        # resize canvas scrollregion
        canvas.config(scrollregion=(0, 0, w * cell_size, h * cell_size))
        # save draw params
        self._cell_draw_params = dict(cell_size=cell_size, rows=h, cols=w, amin=amin, amax=amax)

        # re-highlight selected cell if present
        if self._selected_cell is not None:
            self._highlight_cell(self._selected_cell[0], self._selected_cell[1], color='green')
        if self._selected_cell2 is not None:
            self._highlight_cell(self._selected_cell2[0], self._selected_cell2[1], color='green')

    def _on_cell_click(self, event):
        """Handle click on canvas: compute row/col, highlight and process."""
        if not hasattr(self, '_cell_draw_params'):
            return
        params = self._cell_draw_params
        sz = params['cell_size']
        col = int(event.x / sz)
        row = int(event.y / sz)
        # bounds check
        if row < 0 or row >= params['rows'] or col < 0 or col >= params['cols']:
            return
        try:
            arr = np.array(self.map)
        except Exception:
            return
        if not arr[row, col]:
            return
        # store selection
        prev = self._selected_cell
        self._selected_cell = (row, col)
        # remove previous highlight
        if prev is not None:
            self._remove_highlight(prev[0], prev[1])
        # highlight new
        self._highlight_cell(row, col, color='green')
        # process selection: update UI labels
        try:
            val = float(self.map[row, col])
        except Exception:
            val = None
        self.origin_label.set(f"{row},{col}")
        self.calculate_dijkstra()

    def _on_cell_right_click(self, event):
        """Handle right click on canvas: compute row/col, highlight and process."""
        if not hasattr(self, '_cell_draw_params'):
            return
        params = self._cell_draw_params
        sz = params['cell_size']
        col = int(event.x / sz)
        row = int(event.y / sz)
        # bounds check
        if row < 0 or row >= params['rows'] or col < 0 or col >= params['cols']:
            return
        try:
            arr = np.array(self.map)
        except Exception:
            return
        if not arr[row, col]:
            return
        # store selection
        prev = self._selected_cell2
        self._selected_cell2 = (row, col)
        # remove previous highlight
        if prev is not None:
            self._remove_highlight(prev[0], prev[1])
        # highlight new
        self._highlight_cell(row, col, color='red')
        # process selection: update UI labels
        try:
            val = float(self.map[row, col])
        except Exception:
            val = None
        self.final_label.set(f"{row},{col}")
        self.calculate_dijkstra()


    def _highlight_cell(self, row, col, color='red'):
        canvas = self.cell_canvas
        params = self._cell_draw_params
        sz = params['cell_size']
        x1 = col * sz
        y1 = row * sz
        x2 = x1 + sz
        y2 = y1 + sz
        # draw an outline rectangle on top with tag 'sel'
        canvas.create_rectangle(x1, y1, x2, y2, outline=color, width=2, tags=('sel', f'sel_{row}_{col}'))

    def _remove_highlight(self, row, col):
        canvas = self.cell_canvas
        tag = f'sel_{row}_{col}'
        canvas.delete(tag)

    def calculate_dijkstra(self):
        if self._selected_cell is None or self._selected_cell2 is None:
            return
        start = self._selected_cell
        end = self._selected_cell2
        t1=datetime.now()
        # Implement Dijkstra's algorithm here
        path = self.dijkstra.planning(start, end)
        t2=datetime.now()
        self.dtime_label.set(str(t2-t1))
        # print( path)
        if path is None:
            self.distance_label.set(f"Null")
            self.number_of_nodes.set(f"Null")
            return
        self.distance_label.set(f"{len(path)}")
        if self.algo == "syanes":
            refined_path = reduce_path(path, self.obstacle_map)
        elif self.algo == "bressen":
            refined_path = reduce_path_bresenham(path, self.obstacle_map)
        elif self.algo == "douglas_peucker":
            refined_path = reduce_path_douglas_peucker(path, self.obstacle_map)
        elif self.algo == "new_syanes":
            refined_path = reduce_path_new(path, self.obstacle_map)
        t3 = datetime.now()
        print(f"rendering {self.algo}")
        # Update number_of_nodes and distance_label accordingly
        self.dtime2_label.set(str(t3-t1))
        self.number_of_nodes.set(f"{len(refined_path)}")
        #plot path
        self.cell_canvas.delete('path')
        self.cell_canvas.delete('refpath')
        params = self._cell_draw_params
        sz = params['cell_size']
        for i in range(len(path)-1):
            r1, c1 = path[i]
            r2, c2 = path[i+1]
            x1 = c1 * sz + sz//2
            y1 = r1 * sz + sz//2
            x2 = c2 * sz + sz//2
            y2 = r2 * sz + sz//2
            self.cell_canvas.create_line(x1, y1, x2, y2, fill='red', width=2, tags=('path',))

        for i in range(len(refined_path)-1):
            r1, c1 = refined_path[i]
            r2, c2 = refined_path[i+1]
            x1 = c1 * sz + sz//2
            y1 = r1 * sz + sz//2
            x2 = c2 * sz + sz//2
            y2 = r2 * sz + sz//2
            self.cell_canvas.create_line(x1, y1, x2, y2, fill='blue', width=2, tags=('refpath',))

