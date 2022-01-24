'''
Footer frame.
'''
import tkinter as tk
from tkinter import ttk


class Footer(tk.Frame):
    '''
    Footer frame class.
    '''
    def __init__(self, root: object, container: object):
        self.root, self.container = root, container
        tk.Frame.__init__(self, self.container)
        self.columnconfigure(0, weight=1)
        self.configure(borderwidth=0, pady=10, bg=self.root.style.colors["bg"])

        # Public methods: set message

        self._label_l = None
        self._label_r = None

        self.fill()
        self.set_text = Text(self)

    @property
    def label_l(self) -> object:
        '''
        Get left label widget
        '''
        return self._label_l

    @property
    def label_r(self) -> object:
        '''
        Get right label widget
        '''
        return self._label_r

    def fill(self) -> None:
        '''
        Load widgets.
        '''
        self.columnconfigure(0, weight=1)
        self._label_l = ttk.Label(self, text="Footer")
        self._label_l.grid(row=0, column=0, sticky="W")

        self._label_r = ttk.Label(self, text="Footer")
        self._label_r.grid(row=0, column=1, sticky="E")

class Text():
    '''
    Class for changing footer text.
    '''
    def __init__(self, frame):
        self.frame = frame

    def left(self, text: str) -> None:
        '''
        Set left footer text.
        '''
        self.frame.label_l.configure(text=text)

    def right(self, text: str) -> None:
        '''
        Set right footer text.
        '''
        self.frame.label_r.configure(text=text)
