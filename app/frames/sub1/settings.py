'''
Menu frame
'''
import os
import sys
import json
import tkinter as tk
from tkinter import ttk

import __main__
from app import config, state
from app.frames.views import views_set


class Settings(tk.Toplevel):
    '''
    First start frame class
    '''
    def __init__(self, root: object, container: object):
        self.root, self.container = root, container
        tk.Toplevel.__init__(self, self.container)
        self.title(" - ".join([self.root.wtitle, "Settings"]))
        self.root.center_child(self, (360, 400))
        if state.platform != "win32":
            self.attributes('-type', 'dialog')
        self._colors = self.root.style.colors
        self.configure(padx=10, pady=10, bg=self._colors["bg"])
        self.bind("<Escape>", self._quit_window)

        self._config_changed = {}
        self._view_var = tk.IntVar()
        self._colors_var = tk.IntVar()
        # Copy settings for comparing
        self._default_view = state.app_settings["default_view"]
        self._style_color = state.app_settings["style_color"]
        self._columns_show = state.app_settings["columns_show"][:]

        self._fill()

    def _fill(self) -> None:
        '''
        Load widgets.
        '''
        self.columnconfigure(0, weight=1)

        # Frame left
        left_frame = tk.Frame(self, bg=self._colors["bg"])
        left_frame.grid(row=0, column=0, padx=10, sticky="NW")
        self._fill_left_frame(left_frame)

        # Frame right
        right_frame = tk.Frame(self, bg=self._colors["bg"])
        right_frame.grid(row=0, column=1, padx=10, sticky="NW")
        self._fill_right_frame(right_frame)

        # Bottom widgets
        bottom_frame = tk.Frame(self, bg=self._colors["bg"])
        bottom_frame.grid(row=1, column=0, columnspan=2, padx=10)
        self._fill_bottom_frame(bottom_frame)

    def _fill_left_frame(self, left_frame) -> None:
        '''
        Create widgets for left frame.
        '''
        columns_frame = tk.LabelFrame(left_frame, text="Columns to show",
            bg=self._colors["bg"], fg=self._colors["fg"])
        columns_frame.grid(row=0, column=0, ipadx=10, ipady=4, sticky="W")
        for idx, value in enumerate(self._columns_show):
            if idx in (0, 1, 12, 13): # Exclude some columns
                continue
            col_var = tk.IntVar()
            ttk.Checkbutton(columns_frame, text=config.columns[idx][1],
                variable=col_var, command=self._changed_columns(
                col_var, idx)).grid(row=idx, column=0, sticky="W")
            col_var.set(self._columns_show[value])

    def _fill_right_frame(self, right_frame: object) -> None:
        '''
        Create widgets for right frame.
        '''
        view_frame = ttk.LabelFrame(right_frame, text="Default view")
        view_frame.grid(row=0, column=0, ipadx=10, ipady=4, sticky="WE")
        for idx, (name_, _) in enumerate(views_set):
            ttk.Radiobutton(view_frame, text=name_, value=idx,
                command=self._changed_view, variable=self._view_var).grid(
                row=idx, column=0, padx=10, pady=4, sticky="NW")
        self._view_var.set(state.app_settings["default_view"])

        colors_frame = ttk.LabelFrame(right_frame, text="Interface colors")
        colors_frame.grid(row=1, column=0, ipadx=10, ipady=4,
            pady=20, sticky="WE")
        for idx, name_ in enumerate(self.root.style.get_colors_set()):
            ttk.Radiobutton(colors_frame, text=name_, value=idx,
                command=self._changed_colors, variable=self._colors_var).grid(
                row=idx, column=0, padx=10, pady=4, sticky="NW")
        self._colors_var.set(state.app_settings["style_color"])

        ttk.Button(right_frame, text="Open library",
            command=self._open_library).grid(row=2, column=0)

    def _fill_bottom_frame(self, bottom_frame: object) -> None:
        '''
        Create widgets for bottom frame.
        '''
        ttk.Label(bottom_frame, wraplength=312, text=' '.join(
            ["Library path:", state.app_settings["lib_path"]])).grid(
            row=0, column=0, pady=10, sticky="W")
        ttk.Button(bottom_frame, text="Close",
            command=self._quit_window).grid(row=1, column=0, pady=10)

    def _changed_view(self) -> None:
        '''
        Change default view of books.
        '''
        view_value = self._view_var.get()
        state.app_settings["default_view"] = view_value
        if view_value == self._default_view:
            self._config_changed["default_view"] = False
        else:
            self._config_changed["default_view"] = True

    def _changed_colors(self) -> None:
        '''
        Change default view of books.
        '''
        colors_value = self._colors_var.get()
        state.app_settings["style_color"] = colors_value
        if colors_value == self._style_color:
            self._config_changed["style_color"] = False
        else:
            self._config_changed["style_color"] = True
            mbox = tk.messagebox.askyesno(title="Change interface colors",
                message="Reload Booklib to change colors?")
            if not mbox:
                return
            self._save_settings()
            os.execl(sys.executable, os.path.abspath(__main__.__file__), *sys.argv)

    def _changed_columns(self, col_var: object, col_idx: int) -> callable:
        '''
        Return wrapper for changing column show state in books table.
        '''
        def wrapper() -> None:
            '''
            Change column show state for books table.
            '''
            col_var_value = col_var.get()
            state.app_settings["columns_show"][col_idx] = col_var_value
            if col_var_value == self._columns_show[col_idx]:
                self._config_changed["columns_show"] = False
            else:
                self._config_changed["columns_show"] = True
        return wrapper

    @staticmethod
    def _open_library() -> None:
        '''
        Open other library.
        '''
        mbox = tk.messagebox.askyesno(title="Open library",
            message=''.join(["Are you sure to open other library?\n",
            "Program will be restarted."]))
        if not mbox:
            return
        os.remove(state.app_settings_file)
        os.execl(sys.executable, os.path.abspath(__main__.__file__), *sys.argv)

    def _quit_window(self, event: object = None) -> None:
        '''
        Close window and save base config if it's changed.
        '''
        self._save_settings()
        if any(x for x in self._config_changed.values()):
            self.root.update_view() # Update books frame
            self.root.show_message.success("Settings saved")
        self.destroy()

    def _save_settings(self):
        if any(x for x in self._config_changed.values()):
            with open(state.app_settings_file, "w", encoding="utf-8") as file:
                json.dump(state.app_settings, file, indent=4)
