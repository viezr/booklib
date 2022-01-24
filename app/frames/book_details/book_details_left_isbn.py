'''
Book details frame.
'''
from re import fullmatch
import tkinter as tk
from tkinter import ttk


class BookDetailsLeftISBN(tk.Frame):
    '''
    Book details frame class.
    '''
    def __init__(self, root: object, container: object):
        self.root, self.container = root, container
        tk.Frame.__init__(self, self.container)
        self.configure(bg=self.root.style.colors["bg"])
        self.columnconfigure(0, weight=1)

        # Public methods: update_authors_field only for authors frame

        self._isbn_entry = None
        self._isbn_var = tk.StringVar()
        self._book_changes = {}
        self._book = self.container.book
        self._col_w = 15 # left frame column 0 width

        self._fill()

    def _fill(self) -> None:
        '''
        Load widgets.
        '''
        ttk.Label(self, text="ISBN number", width=self._col_w).grid(
            row=0, column=0, sticky="W")
        self._isbn_entry = ttk.Entry(self, textvariable=self._isbn_var,
            width=20)
        self._isbn_var.set(self._book.isbn)
        self._isbn_entry.grid(row=0, column=1, sticky="W")

    def _update_check_isbn(self) -> bool:
        '''
        Check ISBN field changes and set changes for book update.
        '''
        isbn = self._isbn_var.get()
        pattern = r'^(\w*-*)*$'
        if not fullmatch(pattern, isbn):
            self.root.bad_entry(self._isbn_entry)
            return False
        if str(self._book.isbn) != isbn:
            self._book_changes["isbn"] = isbn
        return True

    def get_updated_fields(self) -> [dict, None]:
        '''
        Return fields changes or None.
        '''
        self._book_changes = {} # Clear changes
        if not self._update_check_isbn():
            return None

        return self._book_changes
