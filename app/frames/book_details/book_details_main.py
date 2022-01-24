'''
Book details frame.
'''
from os import path
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd

from app import state
from app.frames.sub2 import Preview
from .book_details_left import BookDetailsLeft


class BookDetails(tk.Toplevel):
    '''
    Book details frame class.
    '''
    def __init__(self, root: object, container: object):
        self.root, self.container = root, container
        tk.Toplevel.__init__(self, self.container)
        self.title(" - ".join([self.root.wtitle, "Book details"]))
        self.root.center_child(self, (696, 440))
        if state.platform != "win32":
            self.attributes('-type', 'dialog')
        self.configure(padx=10, pady=10, bg=self.root.style.colors["bg"])
        self.bind("<Escape>", self._quit_window)

        # Public methods: authors_changed only for left frame

        self._left_frame = None
        self._preview_frame = None
        self._child_changed = False # Changes state for authors or cover
        self._book = state.sel_books[0]
        self._fill()

    @property
    def book(self) -> object:
        '''
        Return book object of this details window.
        '''
        return self._book

    def authors_changed(self) -> None:
        '''
        Set _child_changed if changes in authors frame.
        '''
        self._child_changed = True

    def _fill(self) -> None:
        '''
        Load widgets.
        '''
        colors = self.root.style.colors
        self.columnconfigure(0, weight=1)

        self._left_frame = BookDetailsLeft(self.root, self)
        self._left_frame.grid(row=0, column=0, sticky="NW")

        right_frame = tk.Frame(self, bg=colors["bg"])
        right_frame.grid(row=0, column=1, sticky="NE")
        self._fill_right_frame(right_frame)

        bottom_frame = tk.Frame(self, bg=colors["bg"])
        bottom_frame.grid(row=1, column=0, columnspan=2, pady=14)
        self._fill_bottom_frame(bottom_frame)

    def _fill_right_frame(self, right_frame: object):
        '''
        Fill right frame.
        '''
        self._preview_frame = Preview(self.root, right_frame,
            book=self._book)
        self._preview_frame.grid(row=0, column=0)
        ttk.Button(right_frame, text="Change cover", command=self._change_cover,
            width=14).grid(row=1, column=0, pady=20)

    def _fill_bottom_frame(self, bottom_frame: object):
        '''
        Fill bottom frame.
        '''
        ttk.Label(bottom_frame, text=" ".join(["There is no need",
            "to update if you change authors or cover."])).grid(
            row=0, column=0, columnspan=2)
        ttk.Button(bottom_frame, text="Update",
            command=self._update_book).grid(row=1, column=0, pady=(20, 0))
        ttk.Button(bottom_frame, text="Close",
            command=self._quit_window).grid(row=1, column=1, pady=(20, 0))

    def _change_cover(self) -> None:
        '''
        Change cover.
        '''
        file = fd.askopenfilename(title = 'Open a file',
            initialdir=path.expanduser("~/"),
            filetypes = [("Images", "*.jpg *.jpeg *.png")])
        if not file:
            self.root.show_message.warning("No file")
            return
        new_cover = ''.join([path.splitext(self._book.file)[0], ".png" ])
        self.root.fd_funcs.change_cover_file(file, new_cover)
        if not self._book.cover:
            self._book.cover = new_cover
            self.root.db_funcs.update_item(self._book, {"cover": new_cover})

        self._preview_frame.clear_cache_img(self._book)
        self._preview_frame.update_img(self._book)
        self.root.update_side_preview()
        self._child_changed = True

    def _update_book(self) -> None:
        '''
        Update book data by changed fields.
        Check fileds and set changes in self._book_changes dict.
        '''
        left_frame_updates = self._left_frame.get_updated_fields()
        if not left_frame_updates:
            return
        # Update book details in database from self._book_changes
        self.root.db_funcs.update_item(self._book, left_frame_updates)

        # clear selected book to renew selected book object
        state.sel_books = state.last_select = None
        self.root.show_message.success("Book updated")
        self.root.update_view() # Update books view
        self.destroy() # Close window

    def _quit_window(self, event: object = None) -> None:
        '''
        Close window and update books if authors or cover were changed.
        '''
        if self._child_changed:
            self.root.update_view()
        self.destroy()
