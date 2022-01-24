'''
Book details frame.
'''
import tkinter as tk
from tkinter import ttk
from datetime import datetime

from app.frames.sub2 import BookAuthors
from .book_details_left_tags import BookDetailsLeftTags
from .book_details_left_read import BookDetailsLeftRead
from .book_details_left_rating import BookDetailsLeftRating
from .book_details_left_pubdate import BookDetailsLeftPubdate
from .book_details_left_isbn import BookDetailsLeftISBN


class BookDetailsLeft(tk.Frame):
    '''
    Book details frame class.
    '''
    def __init__(self, root: object, container: object):
        self.root, self.container = root, container
        tk.Frame.__init__(self, self.container)
        self.configure(bg=self.root.style.colors["bg"])
        self.columnconfigure(0, weight=1)

        # Public methods: update_authors_field only for authors frame

        self._title_entry = None
        self._title_var = tk.StringVar()
        self._authors_entry = None
        self.authors_var = tk.StringVar() # public for main frame
        self._bookmark_btn = None
        self._bookmark_var = tk.IntVar()
        self._child_changed = False # Changes state for authors or cover
        self._book_changes = {}
        self._book = self.container.book
        self._col_w = 15 # left frame column 0 width

        self._fill()

    @property
    def book(self) -> object:
        '''
        Return book object of this details window.
        '''
        return self._book

    def _fill(self) -> None:
        '''
        Load widgets.
        '''
        colors = self.root.style.colors
        pady = (0, 12)
        self.title_frame = tk.Frame(self, bg=colors["bg"])
        self.title_frame.grid(row=0, column=0, sticky="W", pady=pady)
        self. _create_title_field()

        self.authors_frame = tk.Frame(self, bg=colors["bg"])
        self.authors_frame.grid(row=1, column=0, sticky="W", pady=pady)
        self._create_authors_field()

        self.tags_frame = BookDetailsLeftTags(self.root, self)
        self.tags_frame.grid(row=2, column=0, sticky="W")

        self.read_frame = BookDetailsLeftRead(self.root, self)
        self.read_frame.grid(row=3, column=0, sticky="W", pady=pady)

        self.pubdate_frame = BookDetailsLeftPubdate(self.root, self)
        self.pubdate_frame.grid(row=4, column=0, sticky="W", pady=pady)

        self.isbn_frame = BookDetailsLeftISBN(self.root, self)
        self.isbn_frame.grid(row=5, column=0, sticky="W", pady=pady)

        self.time_frame = tk.Frame(self, bg=colors["bg"])
        self.time_frame.grid(row=6, column=0, sticky="W", pady=pady)
        self._create_time_field()

        self.rating_frame = BookDetailsLeftRating(self.root, self)
        self.rating_frame.grid(row=7, column=0, sticky="W", pady=pady)

        self.bookmark_frame = tk.Frame(self, bg=colors["bg"])
        self.bookmark_frame.grid(row=8, column=0, sticky="W", pady=pady)
        self._create_bookmark_field()

    def _create_title_field(self) -> None:
        '''
        Create title field.
        '''
        ttk.Label(self.title_frame, text="Title", width=self._col_w).grid(
            row=0, column=0, sticky="W")
        self._title_entry = ttk.Entry(self.title_frame, textvariable=self._title_var,
            width=41)
        self._title_entry.grid(row=0, column=1, sticky="W")
        self._title_entry.focus_set()
        self._title_var.set(self.book.title)

    def _create_authors_field(self) -> None:
        '''
        Create authors field. Load authors concatenated.
        '''
        authors = self.root.db_funcs.get_authors(self.book.dbid)
        ttk.Label(self.authors_frame, text="Authors", width=self._col_w
            ).grid(row=0, column=0, sticky="W")
        self._authors_entry = ttk.Entry(self.authors_frame,
            textvariable=self.authors_var,
            state="disabled", style="Authors.TEntry", width=30)
        self._authors_entry.grid(row=0, column=1, sticky="W")
        self.authors_var.set(authors)
        ttk.Button(self.authors_frame, text="Change", width=8,
            command=lambda: BookAuthors(self.root, self), style="Field.TButton"
            ).grid(row=0, column=2, padx=16, sticky="W")

    def _create_time_field(self) -> None:
        '''
        Create time-created field.
        '''
        dtime = datetime.fromisoformat(self.book.time_created).astimezone()
        dtime = dtime.strftime("%Y:%m:%d %H:%M:%S")
        ttk.Label(self.time_frame, text="Created date:",
            width=self._col_w).grid(row=0, column=0, sticky="W")
        ttk.Label(self.time_frame, text=dtime).grid(row=0, column=1,
            sticky="W")

    def _create_bookmark_field(self) -> None:
        '''
        Create bookmark field.
        '''
        ttk.Label(self.bookmark_frame, text="Bookmark",
            width=self._col_w).grid(row=0, column=0, sticky="W")
        self._bookmark_btn = ttk.Button(self.bookmark_frame,
            text="Set bookmark", command=self._change_bookmark, width=14)
        self._bookmark_btn.grid(row=0, column=1, sticky="W")
        # set bookmark variable from book
        self._bookmark_var.set(1 if self.book.bookmark == 0 else 0)
        self._change_bookmark()

    def _change_bookmark(self) -> None:
        '''
        Set book to bookmarks.
        '''
        next_ = 1 if self._bookmark_var.get() == 0 else 0
        self._bookmark_var.set(next_)
        self._bookmark_btn.configure(
            text="Set bookmark" if next_ == 0 else "Bookmark",
            style="Mark.TButton" if next_ == 1 else "TButton")

    def update_authors_field(self) -> None:
        '''
        Update authors field.
        '''
        authors = self.root.db_funcs.get_authors(self.book.dbid)
        self.authors_var.set(authors)
        self.container.authors_changed()

    def _check_title(self) -> bool:
        '''
        Check title lenght.
        '''
        title = self._title_var.get()
        if not title.strip() or len(title.strip()) < 2:
            self.root.bad_entry(self._title_entry)
            return False
        if not self.book.title == title:
            self._book_changes["title"] = title
        return True

    def get_updated_fields(self) -> [dict, None]:
        '''
        Check updates in fileds and return changes.
        '''
        self._book_changes = {} # Clear changes
        # Check title changes
        if not self._check_title():
            return None
        # Check bookmark changes
        bookmark = self._bookmark_var.get()
        if not bookmark == self.book.bookmark:
            self._book_changes["bookmark"] = bookmark
        # Check changes in other fields.
        updates = []
        for i in (self.tags_frame, self.read_frame, self.rating_frame,
            self.pubdate_frame, self.isbn_frame):
            updates.append(i.get_updated_fields())

        if any(x is None for x in updates):
            return None
        for i in updates:
            self._book_changes.update(i)
        if not self._book_changes:
            self._book_changes = {} # Clear changes
            return None

        return self._book_changes
