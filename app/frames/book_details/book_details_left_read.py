'''
Book details frame.
'''
import tkinter as tk
from tkinter import ttk

from app import state


class BookDetailsLeftRead(tk.Frame):
    '''
    Book details frame class.
    '''
    def __init__(self, root: object, container: object):
        self.root, self.container = root, container
        tk.Frame.__init__(self, self.container)
        self.configure(bg=self.root.style.colors["bg"])
        self.columnconfigure(0, weight=1)

        # Public methods: update_authors_field only for authors frame

        self._page_var = tk.IntVar()
        self._pages_var = tk.IntVar()
        self._page_entry = None
        self._pages_entry = None
        self._read_state = None
        self._book = self.container.book

        self._fill()

    def _fill(self) -> None:
        '''
        Load widgets.
        '''
        ttk.Label(self, text="Read process", width=15).grid(
            row=0, column=0)

        val_frame = tk.Frame(self, bg=self.root.style.colors["bg"])
        val_frame.grid(row=0, column=1)
        # Widths for next 3 widgets
        w_set = (8, 5, 8) if state.platform != "win32" else (10, 10, 10)
        self._page_entry = ttk.Entry(val_frame, textvariable=self._page_var,
            width=w_set[0], validate="key",
            validatecommand=(self.register(self._page_validation), '%P'))
        self._page_entry.grid(row=0, column=0, sticky="W")
        self._page_var.set(self._book.read_state)

        ttk.Label(val_frame, text="of", anchor="center", width=w_set[1]).grid(
            row=0, column=1)

        self._pages_entry = ttk.Entry(val_frame, textvariable=self._pages_var,
            width=w_set[2], validate="key",
            validatecommand=(self.register(self._pages_validation), '%P'))
        self._pages_entry.grid(row=0, column=2, sticky="W")
        self._pages_var.set(self._book.pages)

        ttk.Label(val_frame, text="Pages").grid(
            row=0, column=3, padx=24, sticky="W")

        self._read_state = ttk.Label(val_frame, style="ReadPerc.TLabel")
        self._read_state.grid(row=0, column=4, padx=(20, 0), sticky="W")
        self._set_read_percent(self._book.read_state, self._book.pages)

    def _pages_validation(self, value: str) -> bool:
        page = self._page_var.get()
        if len(value) > 1 and value.startswith("0"):
            return False
        if not value.isdecimal() or int(value) not in range(1, 10000):
            return False
        self._set_read_percent(page, int(value))
        return True

    def _page_validation(self, value: str) -> bool:
        if not value:
            self._page_var.set(0)
            return True
        pages = self._pages_var.get()
        if len(value) > 1 and value.startswith("0"):
            return False
        if not value.isdecimal() or int(value) not in range(0, pages + 1):
            return False
        self._set_read_percent(int(value), pages)
        return True

    def _set_read_percent(self, page: int, pages: int) -> None:
        if pages == 0 or page not in range(1, pages + 1):
            return
        text = ''.join([str(int(page / (pages / 100))), "%"])
        self._read_state.configure(text=text)

    def get_updated_fields(self) -> [dict, None]:
        '''
        Return fields changes or None.
        '''
        book_changes = {}
        pages, page = self._pages_var.get(), self._page_var.get()
        if pages != self._book.pages:
            book_changes["pages"] = pages
        if page != self._book.read_state:
            book_changes["read_state"] = page

        return book_changes
