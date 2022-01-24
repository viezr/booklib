'''
Content frame
'''
import tkinter as tk

from app import state
from .sub1 import Side
from .views import views_set


class Content(tk.Frame):
    '''
    Content frame class
    '''
    def __init__(self, root: object, container: object):
        self.root, self.container = root, container
        tk.Frame.__init__(self, self.container)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.side_frame=Side(self.root, self)
        self.side_frame.grid(row=0, column=0, sticky="NWSE")
        default_view = state.app_settings["default_view"]
        self.books_frame=views_set[default_view][1](self.root, self)
        self.books_frame.grid(row=0, column=1, sticky="NSWE")
