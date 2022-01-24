'''
Search frame.
'''
import tkinter as tk
from tkinter import ttk

from app import state


class Search(tk.Frame):
    '''
    Search frame class.
    '''
    def __init__(self, root: object, container: object):
        self.root, self.container = root, container
        tk.Frame.__init__(self, self.container)
        self.colors = self.root.style.colors
        self.configure(borderwidth=0, bg=self.colors["bg"])

        # search values - (database column, combobox item name)
        self._search_values = (("title", "Title"), ("authors", "Authors"),
            ("rating", "Rating"), ("isbn", "ISBN"),
            ("time_created", "Created date"), ("pub_date", "Publication date"),
            ("duplicates", "Duplicates"))
        self._combo = self._search_var = self._search_entry = None

        self._fill()

    def _fill(self) -> None:
        '''
        Load widgets.
        '''
        label = ttk.Label(self, text="Search")
        label.grid(row=0, column=0, sticky="W")

        self._combo = ttk.Combobox(self, exportselection=0,
            values=[x[1] for x in self._search_values], state="readonly")
        self._combo.grid(row=0, column=1, padx=10, sticky="W")
        self._combo.current(0)
        self._combo.bind("<<ComboboxSelected>>", self._combo_selected)

        self._search_var = tk.StringVar()
        self._search_entry = ttk.Entry(self, textvariable=self._search_var,
            width=40)
        #self._search_var.set()
        self._search_entry.grid(row=0, column=2, padx=(0, 10), sticky="W")
        self._search_entry.bind("<Return>", self._search)
        self._search_entry.bind("<FocusIn>", self._search_focus)

        search_button=ttk.Button(self, text="Search",
            command=self._search, width=6)
        search_button.grid(row=0, column=3, sticky="E")

    def _combo_selected(self, event: object = None) -> None:
        '''
        Clear search entry. Disable entry if duplicates selected.
        '''
        entry_state = "disabled" if self._combo.current() == 6 else "normal"
        self._search_entry.configure(state=entry_state)
        self._search_var.set("")

    def _check_rate_value(self, value: [str, int]) -> int:
        '''
        Check value if rate search selected.
        '''
        try:
            value = int(value)
        except ValueError:
            self.root.bad_entry(self._search_entry)
            return 0
        if value > 5:
            value = round(value/25) + (1 if self._combo.current() == 3 else 0)
        return value

    def _search_focus(self, event: object = None) -> None:
        '''
        Return focus to entry widget.
        '''
        self.after(200, event.widget.focus_set)

    def _search(self, event: object = None) -> None:
        '''
        Update books by search value
        '''
        sel_idx, val = self._combo.current(), self._search_var.get()
        if not val:
            self.root.show_message.info("No value for search")
            return
        val_type = self._search_values[sel_idx][0]
        val = self._check_rate_value(val) if sel_idx == 2 else val
        # Ignore first char because of sqlite LIKE operator behavior
        # for unicode characters.
        val = val[1:] if isinstance(val, str) and not val.isascii() else val
        val = val.replace("'", "''").lower() if isinstance(val, str) else val
        # Update books table
        state.sel_books = state.last_select = state.sel_tag = None
        self.root.content_frame.side_frame.tag = None
        self.root.update_view(search=(val, val_type))
