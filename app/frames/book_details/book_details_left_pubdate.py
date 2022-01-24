'''
Book details frame.
'''
from re import fullmatch
import tkinter as tk
from tkinter import ttk

from app.modules.days_in_month import days_in_month


class BookDetailsLeftPubdate(tk.Frame):
    '''
    Book details frame class.
    '''
    def __init__(self, root: object, container: object):
        self.root, self.container = root, container
        tk.Frame.__init__(self, self.container)
        self.configure(bg=self.root.style.colors["bg"])
        self.columnconfigure(0, weight=1)

        # Public methods: update_authors_field only for authors frame

        self._pub_date_entry = None
        self._pub_date_var = tk.StringVar()
        self._book_changes = {}
        self._book = self.container.book

        self._fill()

    def _fill(self) -> None:
        '''
        Load widgets.
        '''
        ttk.Label(self, text="Publication date", width=15).grid(
            row=0, column=0, sticky="W")
        self._pub_date_entry = ttk.Entry(self, textvariable=self._pub_date_var,
            width=20)
        self._pub_date_var.set(self._book.pub_date)
        self._pub_date_entry.grid(row=0, column=1, sticky="W")
        ttk.Label(self, text="ISO e.g. 2021-03-15").grid(
            row=0, column=2, padx=(37, 0), sticky="W")

    def _update_check_pub_date(self) -> bool:
        '''
        Check publication date field and set changes for book update.
        '''
        value = self._pub_date_var.get()
        match = False
        pattern = r'\b[1-2][0-9]{3}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])\b'
        if value in ('', "0"):
            match = True
        elif fullmatch(pattern, value):
            match = True
            month, day = value[5:7], value[8:]
            check_days = days_in_month(month, value[:4])
            if int(day) > check_days:
                match = False
        if not match:
            self.root.bad_entry(self._pub_date_entry)
            return False
        if str(self._book.pub_date) != value:
            self._book_changes["pub_date"] = value
        return True

    def get_updated_fields(self) -> [dict, None]:
        '''
        Return fields changes or None.
        '''
        self._book_changes = {} # Clear changes
        if not self._update_check_pub_date():
            return None

        return self._book_changes
