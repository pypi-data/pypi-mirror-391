import customtkinter
import tkinter
import tkinter.font
import tkinter.ttk
import os, sys, platform
import signal
import screeninfo
from .assets import Assets
from .shared import SHARED
from .widgets.labels import *
import pandas as pd
from .tabs.trashdetectiontab import TRASHTAB
from .tabs.gausian_process_tab_nomap import GAUSIANSENSORTAB
from .tabs.mission_tab import MISSIONTAB
from .tabs.dijkstratab import DIJKSTRATAB
from .tabs.map_generation_tab import MAP_GENERATORTAB
# from tabs.map_generation_tab import MAP_GENERATORTAB
# import machine this is for hard reset (machine.reset())
version = "v1.0.0"
max_tab_idx = -1
def next_tab_idx():
    global max_tab_idx
    max_tab_idx += 1
    return max_tab_idx
class ACETI_GUI(tkinter.Tk):
    def __init__(self):
        self.platform=platform.system()
            #get platform
        super().__init__()
        #INIT SHAPE  todo:use customTK
        # customtkinter.set_appearance_mode("System")  # Modes: system (default), light, dark
        # customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green
        self.title("ACETI GUI")
        # schedule a rescale after init and keep handle so we can cancel on exit
        self._rescale_handle = self.after(1000, self.rescale) #after init, scale window
        # elif platform.system() == “Windows”:
        self.configure(bg = 'white')
        self.option_add('*tearOff', False)  # Deshabilita submenús flotantes
        self.max_tab_idx = 0

        #VARIABLES FOR FUNCTIONS
        self.fullscreenstate = False
        # create Assets bound to this Tk instance so PhotoImage objects have a master
        self.assets = Assets(master=self)
        self.shared = SHARED()
        # self.toggle_fullscreen()
        # self.toggle_fullscreen()
        #get screen size
        monitors = screeninfo.get_monitors()
        self.screenheight=monitors[0].height
        self.screenwidth=monitors[0].width
        self.screenyoffset=monitors[0].y
        self.screenxoffset=monitors[0].x
        for m in reversed(monitors):
            if m.x <= self.winfo_x() <= m.width + m.x and m.y <= self.winfo_y() <= m.height + m.y:
                self.screenheight=m.height
                self.screenwidth=m.width
                self.screenyoffset=m.y
                self.screenxoffset=m.x

        # Style for white ttk PanedWindow
        self.option_add('*Background', 'white')
        self.option_add('*Foreground', 'black')
        self.option_add('*Button.Background', 'white')
        self.option_add('*Button.Foreground', 'black')
        self.option_add('*Label.Background', 'white')
        self.option_add('*Menu.background', 'white')
        self.option_add('*Menu.foreground', 'black')
        self.option_add('*Menu.activeBackground', '#e6e6e6')

        style = tkinter.ttk.Style()
        style.configure('.', background='white', foreground='black')
        style.configure('TFrame', background='white')
        style.configure('TPanedwindow', background='white')
        style.configure('White.TPanedwindow', background='white')
        style.configure('TLabel', background='white', foreground='black')
        style.configure('TButton', background='white', foreground='black')
        style.configure('TNotebook', background='white')
        style.configure('TNotebook.Tab', background='white')
        style.configure('TCombobox', fieldbackground='white', background='white', foreground='black')
        style.map('TCombobox',
                  fieldbackground=[('readonly', 'white')],
                  background=[('active', 'white'), ('!disabled', 'white')])

        self.mainFrame = tkinter.ttk.PanedWindow(orient="vertical", style='White.TPanedwindow')
        self.mainFrame.pack(side='top', fill='both', expand=True,)
        self.iconphoto(self, self.assets.aceti_icon)

        #menubar
        self.toolbar = tkinter.Frame(self.mainFrame, relief='raised', bd=2, bg="#E5E5E5")
        tkinter.Label(self.toolbar, text=version).pack(side="right", fill='y', padx=0, pady=2)
        
        self.mainFrame.add(self.toolbar)
        self.menubar_buttons=[]

        ####################################################
        ############## different tabs
        ####################################################
        self.tabs=[]
        
        #create trash map tab
        self.button_trash_detection = tkinter.Button(self.toolbar, image=self.assets.icon_water_trash, command=lambda a=next_tab_idx(): self.change_tab(a), width=40, height=40)
        self.button_trash_detection.pack(side='left', expand=False,)
        self.menubar_buttons.append(self.button_trash_detection)   
        self.TRASHTAB = TRASHTAB(parent=self) 
        self.tabs.append(self.TRASHTAB)

        #create gaussian sensor tab
        self.button_gaussian_sensor = tkinter.Button(self.toolbar, image=self.assets.icon_gaussian_process, command=lambda a=next_tab_idx(): self.change_tab(a), width=40, height=40)
        self.menubar_buttons.append(self.button_gaussian_sensor)
        self.button_gaussian_sensor.pack(side='left', expand=False,)
        self.GAUSIANSENSORTAB=GAUSIANSENSORTAB(parent=self)
        self.tabs.append(self.GAUSIANSENSORTAB)

        # create mission tab
        self.button_mission = tkinter.Button(self.toolbar, image=self.assets.icon_path_planning, command=lambda a=next_tab_idx(): self.change_tab(a), width=40, height=40)
        self.menubar_buttons.append(self.button_mission)
        self.button_mission.pack(side='left', expand=False,)
        self.MISSIONTAB = MAP_GENERATORTAB(parent=self)
        self.tabs.append(self.MISSIONTAB)

        self.button_dijkstra = tkinter.Button(self.toolbar, image=self.assets.icon_path_planning, command=lambda a=next_tab_idx(): self.change_tab(a), width=40, height=40)
        self.menubar_buttons.append(self.button_dijkstra)
        self.button_dijkstra.pack(side='left', expand=False,)
        self.DIJKSTRATAB = DIJKSTRATAB(parent=self)
        self.tabs.append(self.DIJKSTRATAB)

        #generate map tab
        # self.map_generation_but = tkinter.Button(self.toolbar, image=self.assets.icon_map_gen, command=lambda a=next_tab_idx(): self.change_tab(a), width=40, height=40)
        # self.menubar_buttons.append(self.map_generation_but)
        # self.map_generation_but.pack(side='left', expand=False,)
        # self.mapgentab = MAP_GENERATORTAB(parent=self)
        # self.tabs.append(self.mapgentab)
        
        #select init tab
        self.change_tab(3)

        #MENU BAR
        menubar = tkinter.Menu(self)
        self['menu']=menubar
        
        filemenu = tkinter.Menu(menubar)
        settings = tkinter.Menu(menubar)
        helpmenu = tkinter.Menu(menubar)
        menubar.add_cascade(menu=filemenu, label='File')
        menubar.add_cascade(menu=settings, label='Settings')
        menubar.add_cascade(menu=helpmenu, label='Help')

        #FILEMENU
        filemenu.add_separator()  # Agrega un separador
        filemenu.add_command(label='Exit', command=self.destroy, 
                            underline=0, accelerator="Ctrl+q",
                            image=self.assets.icon_trash_log, compound='left')

        #KEY BINDS
        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Escape>", self.end_program)
        # ensure we do a clean shutdown when window is closed by the window manager
        self.protocol("WM_DELETE_WINDOW", self.end_program)
        
        #extravars
        boldfont = tkinter.font.Font(weight='bold')



    def toggle_fullscreen(self, event=None):
        self.fullscreenstate = not self.fullscreenstate  # Just toggling the boolean
        self.attributes("-fullscreen", self.fullscreenstate)
        return "break"

    def end_program(self, event=None):
        # attempt graceful shutdown: cancel scheduled 'after' callbacks from tabs and self
        try:
            # prevent re-entrance
            if getattr(self, '_closing', False):
                return "break"
            self._closing = True

            # cancel own rescale callback
            try:
                if hasattr(self, '_rescale_handle') and self._rescale_handle is not None:
                    self.after_cancel(self._rescale_handle)
            except Exception:
                pass

            # cancel known callbacks stored in tabs
            for t in getattr(self, 'tabs', []):
                # common attribute names that hold after handles
                for attr in ('play_callback', 'download_loop_object', 'gp_loop_object', 'after_object', 'mission_loop_object'):
                    try:
                        handle = getattr(t, attr, None)
                        if handle:
                            try:
                                self.after_cancel(handle)
                            except Exception:
                                pass
                            try:
                                setattr(t, attr, None)
                            except Exception:
                                pass
                    except Exception:
                        pass
                # call tab-specific close() if exists
                try:
                    if hasattr(t, 'close'):
                        t.close()
                except Exception:
                    pass

            # final quit/destroy
            try:
                self.quit()
            except Exception:
                pass
            try:
                self.destroy()
            except Exception:
                pass
            # try to explicitly delete image assets and force GC to avoid PIL PhotoImage destructor warnings
            try:
                import gc
                try:
                    if hasattr(self, 'assets'):
                        # remove references to PhotoImage objects
                        for k,v in list(self.assets.__dict__.items()):
                            try:
                                setattr(self.assets, k, None)
                            except Exception:
                                pass
                except Exception:
                    pass
                gc.collect()
            except Exception:
                pass
        except Exception:
            pass
        return "break"

    def dummy(self):
        pass

    def rescale(self, event=None):
        if self.platform == "Linux":
            self.attributes('-zoomed', True)
        else:
            self.state('zoomed')

    def change_tab(self, tab):
        for i in range(len(self.menubar_buttons)):
            if i == tab:
                self.menubar_buttons[tab].config(relief="sunken")
            else:
                self.menubar_buttons[i].config(relief="raised")
        for i in range(len(self.tabs)):
            try:
                if tab==i:
                    self.mainFrame.add(self.tabs[i])
                    self.tabs[i].open()
                else:
                    self.mainFrame.forget(self.tabs[i])
                    self.tabs[i].close()
            except:
                # error= traceback.format_exc()
                # print(f"There was an error oculting tab\n{error}")
                pass

def main(args=None):
    web=ACETI_GUI()
    print(f"Init Version {version}")
    web.mainloop() 
    print("Finishing Application")
    print("Application Finished")
    

if __name__ == '__main__':
    main()
