'''
Book details frame.
'''
import tkinter as tk
from tkinter import ttk

from app import state


class TagDetails(tk.Toplevel):
    '''
    Tag details frame class.
    '''
    def __init__(self, root: object, container: object):
        self.root, self.container = root, container
        tk.Toplevel.__init__(self, self.container)
        self.title(" - ".join([self.root.wtitle, "Tag edit"]))
        self.root.center_child(self, (440, 144))
        self.attributes('-topmost', 'true')
        if state.platform != "win32":
            self.attributes('-type', 'dialog')
        self.configure(padx=10, pady=4, bg=self.root.style.colors["bg"])
        self.bind("<Escape>", self._quit_window)

        self._fill()

    def _fill(self) -> None:
        '''
        Load widgets.
        '''
        col1_w, col1_padx, row_pady, btn_w = 24, 10, 20, 8

        self.entry_var = tk.StringVar()
        self.entry = ttk.Entry(self, textvariable=self.entry_var,
            width=col1_w,)
        self.entry.grid(row=0, column=0, padx=col1_padx, pady=row_pady, sticky="W")
        self.entry_var.set(state.sel_tag.db_name)

        ttk.Button(self, text="Upd", width=btn_w,
            command=self._update_tag).grid(row=0, column=1,
            padx=(col1_padx, 0), sticky="W")

        ttk.Button(self, text="Del", width=btn_w, style="Bad.TButton",
            command=self.root.menu.delete_tag).grid(row=0, column=2,
            padx=(col1_padx, 0), sticky="W")

        ttk.Button(self, text="Close",command=self._quit_window).grid(
            row=1, column=0, columnspan=3, pady=(30, 20))

    def _update_tag(self) -> None:
        '''
        Update tag in database.
        '''
        tag_name = self.entry_var.get()
        tag_name = self.root.check_tag_name(tag_name, state.sel_tag.tag_type)
        if not tag_name:
            return
        self.root.db_funcs.update_item(state.sel_tag,
            {''.join([state.sel_tag.tag_type, "_name"]): tag_name})
        self.root.update_side_tags()
        self.root.show_message.success("Tag updated")
        self.destroy()

    def _quit_window(self, event: object = None) -> None:
        '''
        Close window.
        '''
        self.destroy()
