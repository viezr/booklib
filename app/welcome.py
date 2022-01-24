'''
App first run window.
'''
import json
from os import path, mkdir
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd

from .config import Style


class Welcome(tk.Toplevel):
    '''
    First run frame class.
    '''
    def __init__(self, config_file: str, platform: str):
        tk.Toplevel.__init__(self)
        self._wtitle="Booklib - Welcome"
        self.title(self._wtitle)
        self._set_geometry()
        if platform != "win32":
            self.attributes('-type', 'dialog')
        self.style = Style(1, platform) # Custom styles
        self.configure(padx=10, background=self.style.colors["bg"])
        self.master.withdraw() # Hide empty root window

        self._lib_folder_label = None
        self._lib_default = path.expanduser("~/Booklib")
        self._settings_file = config_file
        self._settings = {}

        self._fill()

    def _set_geometry(self) -> None:
        '''
        Set size and position of window.
        '''
        scr_w, scr_h = self.winfo_screenwidth(), self.winfo_screenheight()
        wnd_w, wnd_h = 480, 240
        self.geometry(''.join([
            str(wnd_w), "x", str(wnd_h), "+",
            str( int((int(scr_w) - wnd_w) / 2) ), "+",
            str( int((int(scr_h) - wnd_h) / 2) )
        ]))

    def _fill(self) -> None:
        '''
        Load content to frame.
        '''
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        ttk.Label(self, anchor="center", padding=10, style = "Title.TLabel",
            text="Please, set directory for books library.").grid(
            row=0, column=0, sticky="WE")

        self._lib_folder_label=ttk.Label(self, anchor="center", padding=10,
            text="Directory not set")
        self._lib_folder_label.grid(row=1, column=0, sticky="WE")

        ttk.Button(self, text="Set folder", padding=10,
            command=self.set_library_folders).grid(row=2, column=0, sticky="WE")

        ttk.Button(self, text="Close", command=self._quit_window).grid(
            row=3, column=0, pady=20, sticky="S")


    def set_library_folders(self) -> None:
        '''
        Ask for library folder for books, covers and database file.
        Only generate config file for library.
        '''
        if not path.exists(self._lib_default):
            mkdir(self._lib_default)
        folder = fd.askdirectory(title = "Choose directory for books library",
            initialdir=self._lib_default)

        new_folder = path.normpath(folder) if folder else self._lib_default
        books_path = path.join(new_folder, "books")
        covers_path = path.join(new_folder, "covers")
        thumbs_path = path.join(new_folder, "thumbs")
        for i in [books_path, covers_path, thumbs_path]:
            if not path.exists(i):
                mkdir(i)
        self._lib_folder_label.configure(text=" ".join(
            ["Library directory:", new_folder]))
        self._settings = {
            "lib_path": new_folder,
            "lib_books": books_path,
            "lib_covers": covers_path,
            "lib_thumbs": thumbs_path,
            "style_color": 1,
            "default_view": 1,
            "columns_show": [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0]
        }
        with open(self._settings_file, "w", encoding="utf-8") as file:
            json.dump(self._settings, file, indent=4)

    def _quit_window(self) -> None:
        '''
        Quit window.
        '''
        self.master.destroy()
