import tkinter
import tkinter.ttk
import tkinter.font
import threading
import math
import numpy as np
from PIL import Image, ImageTk
from ...common_maps.map_creator import MapDownloader
class MapCreationWindow(tkinter.Toplevel):
    """Minimal Toplevel window to be filled by the user later.

    Usage:
        win = MapCreationWindow(parent)
        win.show()
    """
    def __init__(self, parent, title="Map Creator", width=800, height=600, northwest=[0,0], southeast=[0,0], gridsize=1):
        super().__init__(parent)
        self.parent = parent
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.transient(parent)
        self.grab_set()

        # basic layout
        self.main_frame = tkinter.Frame(self)
        self.main_frame.pack(fill="both", expand=True, padx=8, pady=8)

        self.header = tkinter.Label(self.main_frame, text=title, font=tkinter.font.Font(weight='bold', size=14))
        self.header.pack(side="top", pady=(0,8))

        # placeholder area for future widgets
        self.placeholder = tkinter.Label(self.header, text="Downloading map...")
        self.placeholder.pack(side="top",fill="both", expand=True)
        

        self.gridsize = gridsize

        # initialize cell/grid related state to avoid callback AttributeError
        self._cell_items = {}      # map (row,col) -> canvas item id for overlays
        self._cell_active = {}     # map (row,col) -> bool whether dark overlay is active
        self._cell_draw_params = None
        # selection holders used by click handlers
        self._selected_cell = None
        self._selected_cell2 = None
        # canvas used for cell drawing; some helper methods expect self.cell_canvas
        self.canvas = None
        self.cell_canvas = None

        desired_zoom = math.log2((156543.03392 * math.cos(math.radians((northwest[0] + southeast[0]) / 2))) / (self.gridsize)) + 2
        if desired_zoom > 22:
            desired_zoom = 21
        elif desired_zoom < 0:
            desired_zoom = 0
        print(f"to have {self.gridsize} pixels per grid, you need to set zoom to {int(desired_zoom)}")

        if northwest[0]<southeast[0]:
            aux=northwest[0]
            northwest[0]=southeast[0]
            southeast[0]=aux
        if northwest[1]>southeast[1]:
            aux=northwest[1]
            northwest[1]=southeast[1]
            southeast[1]=aux


        self.mapa = MapDownloader(northwest, southeast, zoom=int(desired_zoom), layer="s", server ="arcgis")

        self.tilenumber = abs(self.mapa.nw_tile[0]-self.mapa.se_tile[0]) * abs(self.mapa.nw_tile[1]-self.mapa.se_tile[1])

        #crea una barra de carga de elements divisiones
        self.progress_bar = tkinter.ttk.Progressbar(self.main_frame, mode="determinate", length= 400, maximum=self.tilenumber)
        self.progress_bar.pack(side="top", fill="x", pady=(8,0))
        self.download_thread = threading.Thread(target=self.start_download)
        self.download_thread.start()
        # action buttons
        buttons = tkinter.Frame(self.main_frame)
        buttons.pack(side="bottom", fill="x", pady=(8,0))

        self.cancel_button = tkinter.Button(buttons, text="Cancel", command=self.on_cancel)
        self.cancel_button.pack(side="right")
        self.bind("<Escape>", self.end_program)



    def start_download(self):
        downloader = self.mapa.image_generator()
        # update progress in the Tk thread via after to avoid thread-safety issues
        for _ in downloader:
            try:
                self.after(0, self.progress_bar.step, 1)
            except Exception:
                # fallback to direct call if after fails for any reason
                try:
                    self.progress_bar.step(1)
                except Exception:
                    pass
        self.progress_bar.destroy()
        self.cancel_button.destroy()
        self.placeholder.config(text="Map download complete.")
        self.after(10, self.create_navigation_map)

    def create_navigation_map(self):
        self.latlonmap = self.mapa.create_grid_latlon(self.gridsize)
        self.navigation_map = np.ones_like(self.latlonmap, dtype=np.uint8)
        self.placeholder.config(text="Map and grid created.")

        self.tools_frame = tkinter.Frame(self.main_frame)
        self.tools_frame.pack(side="right", fill="y", padx=(8,0))

        def _validate_int(self, proposed=0):
            """Return True if proposed string is empty or a float with up to 2 decimals."""
            if proposed == "":
                return True
            try:
                m = int(proposed)
                return m is not None
            except Exception:
                return False

        tkinter.Label(self.tools_frame, text="Pincel Size (cells):").pack(side="left", padx=(0, 10))
        self.pinzel_size = tkinter.StringVar()
        self.pinzel_size.set("1")
        vcmd = (self.register(_validate_int), '%P')
        self.pincel_check = tkinter.Entry(self.tools_frame, textvariable=self.pinzel_size)
        self.pincel_check.pack(side="left", padx=(0, 10))
        self.pincel_check.config(validate='key', validatecommand=vcmd)
        self._cell_active = getattr(self, '_cell_active', {})

        #boton de guardar
        self.save_button = tkinter.Button(self.tools_frame, text="Save Navigation Map", command=self.save_navigation_map)
        self.save_button.pack(side="top", pady=(8,0))

        # create a canvas that expands with the window and will display a rescaled map
        if hasattr(self, 'canvas') and self.canvas:
            try:
                # remove previous image item if any
                if hasattr(self, '_image_id'):
                    try:
                        self.canvas.delete(self._image_id)
                    except Exception:
                        pass
            except Exception:
                pass

        self.canvas = tkinter.Canvas(self.main_frame, bg='white')
        self.canvas.pack(side="top", fill="both", expand=True)

        # keep a copy of the original PIL image (we will resize from this on demand)
        try:
            self._orig_map_img = self.mapa.map_img.copy()
        except Exception:
            self._orig_map_img = self.mapa.map_img

        # create initial PhotoImage (will be updated on first configure)
        try:
            self.tk_map_img = ImageTk.PhotoImage(self._orig_map_img)
        except Exception:
            try:
                img = self._orig_map_img.convert('RGBA')
                self.tk_map_img = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Failed to create PhotoImage from map image: {e}")
                return

        # create image on canvas and store its id (will be repositioned on resize)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_map_img)


        # store handler so it can be unbound if needed
        self.canvas.bind('<Configure>', self._on_canvas_config)

        self.canvas.bind('<B1-Motion>', self._on_cell_click)
        self.canvas.bind('<B3-Motion>', self._on_cell_right_click)

        # bind resize handler to rescale the image while keeping aspect ratio
    def _on_canvas_config(self, event=None):
        canvas = self.canvas
        # nothing to do if image/grid not ready
        if not hasattr(self, '_orig_map_img') or not hasattr(self, 'latlonmap'):
            return

        # get canvas size
        c_w = max(canvas.winfo_width(), 2)
        c_h = max(canvas.winfo_height(), 2)

        img_w, img_h = self._orig_map_img.size
        # compute scale to fit image inside canvas while keeping aspect ratio
        scale = min(c_w / img_w, c_h / img_h)
        new_w = max(1, int(img_w * scale))
        new_h = max(1, int(img_h * scale))

        # resize original image to new size
        try:
            resized = self._orig_map_img.resize((new_w, new_h), resample=Image.LANCZOS)
        except Exception:
            resized = self._orig_map_img.copy()

        # create a new PhotoImage and keep reference to avoid GC
        try:
            self.tk_map_img = ImageTk.PhotoImage(resized)
        except Exception:
            try:
                self.tk_map_img = ImageTk.PhotoImage(resized.convert('RGBA'))
            except Exception as e:
                print(f"Failed to create resized PhotoImage: {e}")
                return

        # clear canvas and draw the resized image at top-left (0,0)
        canvas.delete('all')
        self._image_id = canvas.create_image(0, 0, anchor='nw', image=self.tk_map_img)

        # compute grid cell size from the resized image and the latlonmap shape
        w, h = self.latlonmap.shape
        print(f"latlonmap shape: {h} rows x {w} cols, scale: {scale:.5f} image size: {new_w}x{new_h} old {img_w}x{img_h} active cells: {sum(self._cell_active.values())}")
        cell_w = max(1, new_w / w)
        cell_h = max(1, new_h / h)

        # draw rectangles and remember their ids
        self._cell_items = getattr(self, '_cell_items', {})
        self._cell_items.clear()
        for r in range(h):
            y1 = r * cell_h
            y2 = y1 + cell_h
            for c in range(w):
                x1 = c * cell_w
                x2 = x1 + cell_w
                tag = f"cell_{r}_{c}"
                rid = canvas.create_rectangle(x1, y1, x2, y2, outline='lightgrey', width=1, tags=(tag, 'cell'))
                self._cell_items[(r, c)] = rid
                try:
                    if self._cell_active[(r, c)]:
                        self._highlight_cell(r, c, color='gray')
                        print(f"cell {(r,c)} is active", end='')
                except:
                    self._cell_active[(r, c)] = False

        # resize canvas scrollregion
        canvas.config(scrollregion=(0, 0, w * cell_w, h * cell_h))
        # ensure references for other methods
        self.cell_canvas = canvas
        # save draw params
        self._cell_draw_params = dict(cell_w=cell_w, cell_h=cell_h, rows=h, cols=w, img_w=new_w, img_h=new_h, scale=scale)

    def _on_cell_click(self, event):
        """Handle click on canvas: compute row/col, highlight and process."""
        if not hasattr(self, '_cell_draw_params'):
            return
        params = self._cell_draw_params
        _row = int(event.y / params['cell_h'])
        _col = int(event.x / params['cell_w'])
        for row in range(_row - int(self.pinzel_size.get()), _row + int(self.pinzel_size.get())+1):
            for col in range(_col - int(self.pinzel_size.get()), _col + int(self.pinzel_size.get())+1):
                # bounds check
                if row < 0 or row >= params['rows'] or col < 0 or col >= params['cols']:
                    continue
                # highlight new
                self._highlight_cell(row, col, color='gray')
                # process selection: update UI labels
                try:
                    self.navigation_map[row, col] = 0 # mark as non navigable
                except Exception:
                    pass
                self._cell_active[(row, col)] = True

    def _on_cell_right_click(self, event):
        """Handle right click on canvas: compute row/col, highlight and process."""
        if not hasattr(self, '_cell_draw_params'):
            return
        params = self._cell_draw_params

        _row = int(event.y / params['cell_h'])
        _col = int(event.x / params['cell_w'])
        for row in range(_row - int(self.pinzel_size.get()), _row + int(self.pinzel_size.get())+1):
            for col in range(_col - int(self.pinzel_size.get()), _col + int(self.pinzel_size.get())+1):
                # bounds check
                if row < 0 or row >= params['rows'] or col < 0 or col >= params['cols']:
                    continue
                # highlight new
                self._remove_highlight(row, col)
                # process selection: update UI labels
                try:
                    self.navigation_map[row, col] = 1 # mark as non navigable
                except Exception:
                    pass
                self._cell_active[(row, col)] = False


    def _highlight_cell(self, row, col, color='red'):
        if self._cell_active[(row, col)]:
            return  # already active
        canvas = self.canvas
        params = self._cell_draw_params
        sw = params['cell_w']
        sh = params['cell_h']

        x1 = col * sw
        y1 = row * sh
        x2 = x1 + sw
        y2 = y1 + sh
        # draw an outline rectangle on top with tag 'sel'
        canvas.create_rectangle(x1, y1, x2, y2, fill=color, width=2, tags=('sel', f'sel_{row}_{col}'))

    def _remove_highlight(self, row, col):
        if not self._cell_active[(row, col)]:
            return  # already inactive
        canvas = self.canvas
        tag = f'sel_{row}_{col}'
        canvas.delete(tag)

    def on_cancel(self):
        self.destroy()

    def show(self):
        self.wait_window(self)

    def end_program(self, event=None):
        if self.download_thread.is_alive():
            self.download_thread.join(timeout=10)
        self.on_cancel()

    def save_navigation_map(self):
        import tkinter.filedialog

        file_path = tkinter.filedialog.asksaveasfilename(
            parent=self,
            title="Save Navigation Map",
            filetypes=[("Navigation Map Files", "*.npy"), ("All Files", "*.*")],
        )
        if not file_path:
            return  # user cancelled
        
        if ".npy" not in file_path:
            file_path += ".npy"
        np.save(file_path.replace('.npy', 'mask.npy'), self.navigation_map.T)
        np.save(file_path.replace('.npy', 'latlon.npy'), self.latlonmap)
