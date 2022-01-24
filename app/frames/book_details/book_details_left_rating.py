'''
Book details frame.
'''
import tkinter as tk
from tkinter import ttk


class BookDetailsLeftRating(tk.Frame):
    '''
    Book details frame class.
    '''
    def __init__(self, root: object, container: object):
        self.root, self.container = root, container
        tk.Frame.__init__(self, self.container)
        self.configure(bg=self.root.style.colors["bg"])
        self.columnconfigure(0, weight=1)

        # Public methods: update_authors_field only for authors frame

        self._rating_var = tk.IntVar()
        self._rating_vars = []
        self._book = self.container.book
        self._col_w = 15 # left frame column 0 width

        self._fill()

    def _fill(self) -> None:
        '''
        Load widgets.
        '''
        ttk.Label(self, text="Rating", width=self._col_w).grid(row=0, column=0)

        val_frame = tk.Frame(self, bg=self.root.style.colors["bg"])
        val_frame.grid(row=0, column=1)
        for val in range(5):
            rt_var = tk.IntVar()
            ttk.Checkbutton(val_frame, variable=rt_var,
                command=self._set_rating(val + 1), takefocus=False,
                style="Rating.TCheckbutton").grid(row=0, column=val)
            self._rating_vars.append(rt_var)
        if self._book.rating:
            self._set_rating(self._book.rating)()

    def _set_rating(self, val: int) -> callable:
        '''
        Return wrapper for setting book rating.
        '''
        def wrapper() -> None:
            '''
            Set book rating.
            '''
            for i in range(val):
                self._rating_vars[i].set(1)
            for i in range(val, 5):
                self._rating_vars[i].set(0)
            self._rating_var.set(val)
        return wrapper

    def get_updated_fields(self) -> [dict, None]:
        '''
        Return fields changes or None.
        '''
        book_changes = {}
        rating = self._rating_var.get()
        if rating != self._book.rating:
            book_changes["rating"] = rating

        return book_changes
