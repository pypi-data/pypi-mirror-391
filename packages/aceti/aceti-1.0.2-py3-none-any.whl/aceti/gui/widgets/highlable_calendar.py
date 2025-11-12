import tkinter
import tkinter.font
import tkinter.ttk
from tkcalendar import Calendar


class highlable_calendar(Calendar):
    def __init__(self, *args, parent=None, **kwargs):
        self.data_available_list=[]
        self.parent=parent
        super(highlable_calendar, self).__init__(*args, **kwargs)
        self.style.configure('data.%s.TLabel' % self._style_prefixe, background="OliveDrab1",
                             foreground=self._properties.get('normalforeground'))
        self.bind("<<CalendarSelected>>", self.day_selection_callback)

    def _display_calendar(self):
        super()._display_calendar()
        for item in self.data_available_list:
            self.highlight(item)

    def _remove_selection(self):
        if self._sel_date is not None:
            super()._remove_selection()
            if self._sel_date in self.data_available_list:
                self.highlight(self._sel_date)

    def highlight(self,date):
        w, d = self._get_day_coords(date)
        if w is not None:
            label = self._calendar[w][d]
            if label.cget('text'):
                label.configure(style='data.%s.TLabel' % self._style_prefixe)

    def add_to_data(self, date):
        self.configure(state="normal")
        self.data_available_list.append(date)
        if date != self._sel_date:
            self.highlight(date)


    def unhighlight(self):
        self.configure(state="disabled")
        self._display_calendar()

    def day_selection_callback(self, event=None):
        if self.parent is not None:
            if self._sel_date in self.data_available_list:
                self.parent.event_generate("<<UpdatePlotData>>")