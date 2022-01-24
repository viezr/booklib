'''
Books table frame.
'''
import tkinter as tk
from tkinter import ttk

from app import config, state
from app.frames.sub2 import MenuPopup


class BooksTable(tk.Frame):
    '''
    Books table frame class.
    '''
    def __init__(self, root: object, container: object):
        self.root, self.container = root, container
        tk.Frame.__init__(self, self.container)
        self._colors = self.root.style.colors
        self.configure(borderwidth=0, bg=self._colors["bg"])

        self._books_table = None

        # Public methods: update_view

        self._fill()
        self._wait_interface()

    def _wait_interface(self) -> None:
        if not hasattr(self.root, "db_funcs"):
            self.after(50, self._wait_interface)
        else:
            self.update_view()

    def _fill(self) -> None:
        '''
        Load widgets.
        '''
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        ybooks_scroll = ttk.Scrollbar(self, orient="vertical")
        ybooks_scroll.grid(row=0, column=1, sticky="NSE")
        self._books_table = ttk.Treeview(self,yscrollcommand=ybooks_scroll.set,
            takefocus=1, style="Books.Treeview")
        ybooks_scroll.config(command=self._books_table.yview)
        self._books_table.tag_configure("odd",
            background=self._colors["treeview_bg1"])
        self._books_table.tag_configure("even",
            background=self._colors["treeview_bg2"])
        self._books_table["columns"] = [x[0] for x in config.columns]
        self._books_table.bind("<FocusIn>", self._table_focus)

        # format columns
        self._books_table.column("#0", width=50, anchor="w", stretch="no")
        for col in config.columns:
            self._books_table.column(col[0], anchor="w", width=col[2],
                stretch=1 if col[0] == "title" or col[0] == "authors" else 0)

        # Create Headings
        self._books_table.heading("#0",text="#", anchor="center")
        for head in config.columns:
            self._books_table.heading(head[0], text=head[1],
                anchor="center", command=self._sort_by(head[0]))

        self._books_table.bind("<<TreeviewSelect>>", self._select_books)
        self._books_table.bind("<Double-1>", self.root.menu.books_edit)
        self._books_table.bind("<ButtonRelease-3>",
            lambda x: MenuPopup(self.root, self))
        self._books_table.bind("<Return>", self.root.menu.books_edit)
        self._books_table.bind("<Control-Return>", self.root.menu.read_book)
        self._books_table.grid(row = 0, column = 0, sticky = "NSWE")
        self._books_table.focus_set()

    def _table_focus(self, event: object = None):
        '''
        Set focus to last selected book or firs book.
        '''
        frame_tree = self._books_table
        children = frame_tree.get_children()
        last_sel = state.last_select
        if last_sel and last_sel[0] < len(children):
            cur_sel = last_sel[0]
        else:
            cur_sel = self._get_selection_int()
            if cur_sel: # if book selected
                cur_sel = cur_sel[0]
            elif children: # if books in table, set selection to first book
                cur_sel = children[0]
                frame_tree.selection_set(cur_sel) # move selection
            else:
                return
        frame_tree.focus(cur_sel) # move focus
        frame_tree.see(cur_sel) # scroll to show it

    def _sort_by(self, db_column: str) -> None:
        '''
        Sorting books by table header
        '''
        direction = 1
        def wrapper():
            nonlocal direction
            direction = 0 if direction == 1 else 1
            state.last_sort = (db_column, direction)
            self.root.sort_books()
            self.update_view(request=False)
        return wrapper

    def update_view(self, search: tuple = None, request: bool = True) -> None:
        '''
        Get books and update books table. Search sets:
        (search val, col name), (0, "bookmark"), (0, "duplicates")
        '''
        # Request books
        if request:
            self.root.request_books(search = search)

        # Clear books table
        table_children = self._books_table.get_children()
        if table_children:
            self._books_table.delete(*table_children)

        if not state.books:
            return

        col_set = config.columns
        # Set showed columns from config
        self._books_table["displaycolumns"] = [
            x[0] for idx, x in enumerate(col_set)
            if state.app_settings["columns_show"][idx] == 1]

        # Fix mess with columns width then hiding columns (reset widths?)
        for col in config.columns:
            self._books_table.column(col[0], anchor="w", width=col[2])

        # Fill books table
        for i, book in enumerate(state.books):
            values_ = []
            for col_name in book:
                # Format values for some columns
                val = book[col_name] if book[col_name] else ""
                if col_name == "time_created":
                    val = val[:16] if val else ""
                elif col_name == "pub_date":
                    val = val[:4] if val and val != "0" else ""
                elif col_name == "read_state":
                    val = self._read_state(val, book["pages"]) if val else ""
                elif col_name == "bookmark":
                    val = "*" if val == 1 else ""
                values_.append(val)
            self._books_table.insert(parent='', index="end", iid=i, text=i,
                values=values_, tags=("even" if i % 2 == 0 else "odd",))
        self._books_table.update()
        self._table_focus()

    @staticmethod
    def _read_state(page:str, pages:str) -> str:
        text = ""
        page, pages = int(page), int(pages)
        if pages != 0 and page in range(1, pages + 1):
            text = ''.join([str(int(page / (pages / 100))), "%"])
        return text


    def _get_selection_int(self) -> tuple:
        '''
        Get selection and convert iid's from strings to integer.
        '''
        return [int(x) for x in self._books_table.selection()]

    def _select_books(self, event: object) -> None:
        '''
        Load selected book, update preview
        '''
        selection = self._get_selection_int()
        if not selection:
            return
        if selection == state.last_select:
            return
        state.sel_books = []
        for iid in selection:
            book_id = state.books[iid]["book_id"]
            book = self.root.db_funcs.get_book(id_=book_id)
            if book:
                state.sel_books.append(book)

        self.root.update_side_preview()
        self.root.set_footer_text.left(state.sel_books[0].file)

        state.last_select = selection
