'''
Footer frame
'''
import tkinter as tk
from tkinter import ttk


class Info(tk.Frame):
    '''
    Information popup frame class
    '''
    def __init__(self, root: object, container: object):
        self.root, self.container = root, container
        tk.Frame.__init__(self, self.container)
        self.configure(bg=self.root.style.colors["bg"])
        self.columnconfigure(0, weight=1)

        self._after_id = self._label = None

        # Public methods: show_message

        self._fill()
        self.show_message = Message(self)

    def _fill(self) -> None:
        '''
        Load widgets
        '''
        self._label = ttk.Label(self, text="",
            anchor="center")
        self._label.columnconfigure(0, weight=1)
        self._label.grid(row=0, column=0, ipadx=200, ipady=2)

class Message():
    '''
    Class for showing message in info frame.
    '''
    def __init__(self, frame: object):
        self._frame = frame
        self._label = frame._label
        self._after_id = None
        self._styles = ("TLabel", "Info.TLabel", "Good.TLabel", "Bad.TLabel")

    def _set_label(self, text: str, style: int) -> None:
        '''
        Change info frame label text
        '''
        if self._after_id:
            self._frame.after_cancel(self._after_id)
        self._label.configure(text=text, style=self._styles[style])
        self._after_id = self._frame.after(3000, lambda: self._label.configure(
            text='', style=self._styles[0]))

    def info(self, text: str) -> None:
        '''
        Show info message in info frame.
        '''
        self._set_label(text, 1)

    def success(self, text: str) -> None:
        '''
        Show success message in info frame.
        '''
        self._set_label(text, 2)

    def warning(self, text: str) -> None:
        '''
        Show warning message in info frame.
        '''
        self._set_label(text, 3)
