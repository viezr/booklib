'''
Top panel frame.
'''
import tkinter as tk
from tkinter import ttk

from .sub1 import Search, Info


class TopPanel(tk.Frame):
    '''
    Top panel frame class.
    '''
    def __init__(self, root: object, container: object):
        self.root, self.container = root, container
        tk.Frame.__init__(self, self.container)
        self.configure(bg=self.root.style.colors["bg"])
        #self.style = self.root.style

        self._search_frame_hidden = True
        self._fill()

    def _fill(self) -> None:
        '''
        Load widgets.
        '''
        menu = self.root.menu
        btn_funcs = [("Add", menu.add_books_files),
            ("Search", self._search), ("Read", menu.read_book),
            ("Read & Quit", menu.read_quit),
            ("Switch view", menu.switch_view)]

        idx = 0
        for idx, btn_func in enumerate(btn_funcs):
            ttk.Button(self, text=btn_func[0], command=btn_func[1],
                width=len(btn_func[0]) + 1, takefocus=0).grid(
                    row=0, column=idx, padx=(0, 2), sticky="W",)

        self.columnconfigure(idx + 1, weight=1)

        self.info_frame=Info(self.root, self)
        self.info_frame.grid(row=0, column=len(btn_funcs),
            pady=(4, 4), sticky="WE")

        ttk.Button(self, text="Quit", takefocus=0, command=self.root.destroy,
            width=6).grid(row=0, column=len(btn_funcs) + 1, sticky="E")

        self._search_frame = Search(self.root, self)
        self._search_frame.grid(row=1, column=0, pady=(10, 0),
            columnspan=len(btn_funcs) + 1)
        self._search_frame.grid_remove()
        self._search_frame_hidden = True

    def _search(self) -> None:
        '''
        Show/Hide Search frame.
        '''
        if self._search_frame_hidden:
            self._search_frame.grid()
            self._search_frame_hidden = False
            return
        self._search_frame.grid_remove()
        self._search_frame_hidden = True
