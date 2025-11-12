import tkinter
import tkinter.font
import tkinter.ttk

class Checkbox(tkinter.ttk.Checkbutton):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.variable = tkinter.BooleanVar(self)
        self.configure(variable=self.variable)
    
    def checked(self):
        return self.variable.get()
    
    def check(self):
        self.variable.set(True)
    
    def uncheck(self):
        self.variable.set(False)

    def mouse_enter(self,event=None):
        self.set_text(self.name)
        super().mouse_enter(event)
        self.draw()

    def mouse_leave(self, event=None):
        self.set_text("")
        super().mouse_leave(event)

    def leftclick(self, event=None):
        pass
