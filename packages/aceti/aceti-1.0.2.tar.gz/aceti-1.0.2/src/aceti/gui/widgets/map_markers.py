import tkinter
import tkinter.font
import tkinter.ttk
from tkintermapview import TkinterMapView
from PIL import Image, ImageTk
import random
from tkintermapview.canvas_position_marker import CanvasPositionMarker
from tkintermapview.canvas_path import CanvasPath
import matplotlib.pyplot as plt
import matplotlib as mpl


class SHIP(CanvasPositionMarker):
    def __init__(self, name, deg_x: float, deg_y: float,text: str = None, rotation=None, parent=None, *args, **kwargs):
        
        if parent is None:
            super().__init__(self,(deg_x,deg_y),text=text,*args, **kwargs)
            return #stop doing anything


        #store parent
        self.parent=parent
        self.map_widget=parent.map_widget

        #store bag name
        self.name=name
        
        #restore context
        super().__init__(self.map_widget,(deg_x,deg_y), text=text, image_zoom_visibility=(0, float("inf")),  icon=ImageTk.PhotoImage(self.parent.assets.image_ship),command=self.leftclick)
        
        if rotation is not None:
            self.update_rotation(rotation)
        #draw it
        self.draw()
        self.map_widget.canvas_marker_list.append(self)

    def mouse_enter(self,event=None):
        self.set_text(self.name)
        super().mouse_enter(event)
        self.draw()

    def mouse_leave(self, event=None):
        self.set_text("")
        super().mouse_leave(event)

    def leftclick(self, event=None):
        pass

    def update_rotation(self,degrees):
        self.change_icon(ImageTk.PhotoImage(self.parent.assets.image_ship.rotate(degrees)))

class TRASH(CanvasPositionMarker):
    def __init__(self, name, deg_x: float, deg_y: float,text: str = None, parent=None):
        
        if parent is None:
            super().__init__(self,(deg_x,deg_y),text=text,**kwargs)
            return #stop doing anything

        self.max_retain_data=40

        #store parent
        self.parent=parent
        self.map_widget=parent.map_widget
        self.last_value=-200
        #store bag name
        self.name=name
        
        #restore context
        super().__init__(self.map_widget,(deg_x,deg_y), text=text, image_zoom_visibility=(0, float("inf")),command=self.leftclick, icon=self.parent.assets.icon_waste[random.randint(0, self.parent.assets.waste_len-1)])
        
        #draw it
        self.draw()
        self.map_widget.canvas_marker_list.append(self)

    def mouse_enter(self,event=None):
        self.set_text(self.name)
        super().mouse_enter(event)
        self.draw()

    def mouse_leave(self, event=None):
        self.set_text("")
        super().mouse_leave(event)

    def leftclick(self, event=None):
        pass

    def update(self, value):
        if abs(value-self.last_value)>self.max_retain_data:
            self.hide_image(True)
    
    def update_position(self, lat, lon):
        self.hide_image(False)
        self.set_position(lat,lon)



class MEASURE(CanvasPositionMarker):
    def __init__(self, name, deg_x: float, deg_y: float,text: str = None, parent=None, range_=1, min_=0, **kwargs):
        
        if parent is None:
            super().__init__(self,(deg_x,deg_y),text=text,**kwargs)
            return #stop doing anything


        #store parent
        self.parent=parent
        self.map_widget=parent.map_widget
        #store bag name
        self.name=name
        
        #restore context
        # print(f"drawing a measure {((name-min_)*10)//range_}")
        super().__init__(self.map_widget,(deg_x,deg_y), text=text,icon=self.parent.assets.icon_measure[int(((name-min_)*10)//range_)], image_zoom_visibility=(0, float("inf")),command=self.leftclick, text_color="black")
        
        #draw it
        self.draw()
        self.map_widget.canvas_marker_list.append(self)
        if name == 0:
            self.hide_image(True)

    def leftclick(self, event=None):
        try:
            super().leftclick(event)
        except:
            pass

class PATH():
    def __init__(self, df, parent=None, sensor = "ph", **kwargs):
        self.colorlist=["#983604", "#CE3202","#E53602","#FE6501","#FDFC0A","#98CC05","#037F03","#3663FE","#0301CE","#300397","#010263","#030153","#020330","#000000"]
        cmap = mpl.colors.LinearSegmentedColormap.from_list("dummy",self.colorlist)
        self.df = df 
        self.parent=parent
        self.map_widget=parent.map_widget
        self.range=[0,15]
        self.shown_values=0
        self.sensor=sensor
        
        norm = mpl.colors.Normalize(vmin=self.range[0], vmax=self.range[1])
        self.m=mpl.cm.ScalarMappable(norm=norm, cmap=cmap)

        print("we got path")
        self.last_segment=None
        

    def show_up_to(self, value):
        if value == 0:
            value = self.sel_df.index.to_list()[0]
        if value not in self.sel_df.index:
            return
        int_value = self.sel_df .index.to_list().index(value)
        if int_value > self.shown_values:
            for i in self.sel_df.index.to_list()[self.shown_values:int_value]:
                segment=[self.sel_df.loc[i,"Latitude"], self.sel_df.loc[i,"Longitude"]]
                print(segment)
                if self.last_segment is not None:
                    path=CanvasPath(map_widget=self.map_widget,position_list= [segment,self.last_segment] , color=self.get_color(self.sel_df.loc[i,"Data"]), width=4)
                    path.draw()
                    self.map_widget.canvas_path_list.append(path)
                self.last_segment=segment
            self.shown_values=int_value
        else:
            print("resetted list")
            self.map_widget.delete_all_path()
            self.last_segment=None
            self.shown_values=0

        
    def select_sensor(self, sensor:str):
        self.map_widget.delete_all_path()
        self.last_segment=None
        self.shown_values=0
        cmap = mpl.colors.LinearSegmentedColormap.from_list("dummy",self.colorlist)
        self.sel_df=self.df[self.df["Sensor"] == sensor]
        if len(self.sel_df) == 0:
            print("No data for this sensor")
            return
        # Limpiar outliers
        Q1 = self.sel_df['Data'].quantile(0.25)
        Q3 = self.sel_df['Data'].quantile(0.75)
        IQR = Q3 - Q1
        self.sel_df = self.sel_df[~((self.sel_df['Data'] < (Q1 - 3 * IQR)) | (self.sel_df['Data'] > (Q3 + 3 * IQR)))]

        if "ph" in sensor.lower():
            self.range=[0,15]
        else:
            self.range=[min(self.sel_df["Data"]), max(self.sel_df["Data"])]
        norm = mpl.colors.Normalize(vmin=self.range[0], vmax=self.range[1])
        self.m=mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
        self.get_color_map()


    def get_color(self, value):
        value=self.m.to_rgba(value, bytes=True)
        return "#" + '{:02X}'.format(value[0]) + '{:02X}'.format(value[1]) + '{:02X}'.format(value[2])
    
    def get_color_map(self):
        self.parent.colorbar_fig.colorbar(self.m, cax=self.parent.colorbar_ax, orientation='vertical', label='Some Units')
        self.parent.colorbar.draw()
