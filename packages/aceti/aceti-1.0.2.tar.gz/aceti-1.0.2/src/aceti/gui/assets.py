import tkinter
import tkinter.font
import tkinter.ttk
import os, sys
import traceback
from PIL import Image, ImageTk
import requests
from io import BytesIO
import threading


class GIF():
    def __init__(self, file, speed=None, size = 0, master=None):
        self.path=file
        self.loc=0
        self.frames=[]
        self._master = master
        threading.Timer(0,self.__read__,args=(speed,size)).start()
    
    # corrected signature
    def frame(self, index):
        return self.frames[index]

    def get_next_frame(self):
        self.loc=(self.loc+1)%self.len
        return self.frames[self.loc]

    def __read__(self, speed, size):
        self.image=Image.open(self.path)
        if size == 0:
            try:
                n_frames=self.image.n_frames
            except EOFError:
                error= traceback.format_exc()
                print(f"error importing asset gif {self.path}:\n {error}")
                return

        for i in range(n_frames):
            # attach PhotoImage to a master (Tk root) to ensure proper tkinter lifecycle
            m = getattr(self, '_master', None) or tkinter._default_root
            self.frames.append(ImageTk.PhotoImage(self.image.copy(), master=m))
            self.image.seek(i)
        if speed is not None:
            self.delay=1000/speed
        else:
            try:
                self.delay = self.info.duration
            except:
                self.delay = 100

        if len(self.frames)==0:
            return
        self.len=len(self.frames)
        # print(f"gif {path.split('/')[-1]} len {self.len} delay {self.delay}")



class Assets(object):
    def __init__(self, path=None, master=None):
        # master should be the Tk root so PhotoImage objects are attached to it
        self._master = master or tkinter._default_root
        self.path=self.resource_path("assets/")
        # load images (attached to master)
        self.aceti_icon = self.include_image("icon_aceti.png",40,40)
        self.icon_water_trash = self.include_image("icon_water_trash.png",40,40)
        self.icon_trash_log = self.include_image("icon_trash_log.png",40,40)
        self.icon_play = self.include_image("play.png",35,35)
        self.icon_pause = self.include_image("pause.png",35,35)
        self.icon_ship = self.include_image("icon_ship.png",40,40)
        self.icon_gaussian_process = self.include_image("icon_gaussian.png",40,40)
        self.icon_on = self.include_image("on.png",40,20)
        self.icon_off = self.include_image("off.png",40,20)
        self.icon_path_planning = self.include_image("icon_path_planning.png",40,40)
        self.icon_test_big = self.include_image("icon_gaussian.png",400,400)
        self.icon_map_gen = self.include_image("mapgeneration.png",400,400)
        self.icon_lupa = self.include_image("lupa.png",220,220)
        self.map_tiles= self.resource_path("assets/tiles/offline_tiles.db")

        self.image_ship = Image.open(self.path+"icon_ship.png").convert('RGBA').resize((60,60))
        self.waste_len=2
        self.icon_waste=[]
        for i in range(self.waste_len):
            self.icon_waste.append(self.include_image(f"waste{i}.png",40,40))

        self.icon_measure=[]
        for i in range(11):
            self.icon_measure.append(self.include_image(f"measures/{i}.png",10,10))

    def include_image(self,image,sizex,sizey):
        try:
            originalImg = Image.open(self.path+image)
            img= originalImg.resize((sizex, sizey))
            # attach PhotoImage to the supplied master (Tk root) to avoid
            # lifecycle issues during interpreter shutdown
            m = getattr(self, '_master', None) or tkinter._default_root
            return ImageTk.PhotoImage(img, master=m)
        except:
            error = traceback.format_exc()
            print(f"error importing asset {image}:\n {error}")


    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        path = os.path.join(base_path, relative_path)
        if os.path.exists(path):
            return path
        else:#get path of the file
            base_path =  os.path.dirname(__file__)
            path = os.path.join(base_path, "assets")

        if not os.path.exists(base_path):
            raise FileNotFoundError(f"Asset path not found: {base_path}")

        return os.path.join(base_path, relative_path)
    
    def download_image(self, image):
        baseurl="https://fontawesome.com/start"
        response = requests.get(baseurl+"/"+image)
        img = Image.open(BytesIO(response.content))