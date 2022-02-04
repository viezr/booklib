'''
Books shelf frame
'''
import tkinter as tk
from tkinter import ttk

from app import config, state
from app.frames.sub2 import Preview, MenuPopup


class BooksShelf(tk.Frame):
    '''
    Books shelf frame class
    '''
    def __init__(self, root: object, container: object):
        self.root, self.container = root, container
        tk.Frame.__init__(self, self.container)
        self._colors = self.root.style.colors
        self.configure(borderwidth=0, bg=self._colors["bg"])

        self._page = self._pages = 0 # Pagination variables
        self._width = None # Used for calculation columns number
        self._book_blocks = []
        self._book_pad = None

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

        # Canvas
        self._canvas = tk.Canvas(self, bg=self._colors["bg_mid"],
            highlightthickness=0)
        self._canvas.grid(row=0, column=0, sticky="NSWE")

        self._ybooks_scroll = ttk.Scrollbar(self, orient="vertical",
            command=self._canvas.yview)
        self._ybooks_scroll.grid(row=0, column=1, sticky="NSE")
        self._canvas.config(yscrollcommand=self._ybooks_scroll.set)

        self._canvas.rowconfigure(0, weight=1)
        self._books_frame = tk.Frame(self._canvas, bg=self._colors["bg_mid"])
        self._books_frame.grid(row=0, column=0, sticky="NSWE")

        self._books_frame.bind("<Configure>", self._books_changed )
        self._canvas.bind("<Configure>", self._canvas_changed )
        self._books_frame.bind("<MouseWheel>", self._on_mousewheel)
        self._canvas.bind_class("Canvas", "<MouseWheel>", self._on_mousewheel)
        self._canvas.bind_class("Canvas", "<ButtonRelease-3>",
            lambda x: MenuPopup(self.root, self))
        self._canvas.bind_all("<Button-4>", self._on_mousewheel)
        self._canvas.bind_all("<Button-5>", self._on_mousewheel)

        self._content = self._canvas.create_window(
            (0,0), window = self._books_frame, anchor = "nw")

        # Bottom buttons for pagination
        self._buttons_frame = tk.Frame(self, bg=self._colors["bg"])
        self._buttons_frame.grid(row=1, column=0, columnspan=2, pady=10)
        ttk.Button(self._buttons_frame, text="Prev",
            command=self._prev_page).grid(row=0, column=0, sticky="E")
        self._page_label = ttk.Label(self._buttons_frame, text='', width=12,
            anchor="center")
        self._page_label.grid(row=0, column=1)
        ttk.Button(self._buttons_frame, text="Next",
            command=self._next_page).grid(row=0, column=2, sticky="W")

        tk.Frame(self, height=1, bg=self._colors["bg_light"]).grid(
            row=2, column=0, columnspan=2, pady=0, sticky="WE")

        self._books_frame.focus_set()

    def _prev_page(self) -> None:
        '''
        Switch to previous page of books
        '''
        prev = self._pages - 1 if (self._page - 1) < 0 else self._page - 1
        self.update_view(cur_page=prev)

    def _next_page(self) -> None:
        '''
        Switch to next page of books
        '''
        next_ = 0 if (self._page + 1) >= self._pages else self._page + 1
        self.update_view(cur_page=next_)

    def _on_mousewheel(self, event: object) -> None:
        '''
        Scroll books by mousewheel
        '''
        # Return if pointer not at this frame
        if (hasattr(event.widget, "winfo_parent")
            and not "canvas" in event.widget.winfo_parent()):
            return

        # Scroll books
        pos = self._ybooks_scroll.get()
        if event.num == 4 and pos[0] <= 0.0:
            return
        if state.platform == "win32":
            self._canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        else:
            self._canvas.yview_scroll(-1 if event.num == 4 else 1, "units")

    def _books_changed(self, event: object) -> None:
        '''
        Reconfigure canvas on changes in books
        '''
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _canvas_changed(self, event: object) -> None:
        '''
        Rearrange books on window resizing
        '''
        self._canvas.itemconfig(self._content, width = event.width)
        self._arrange_book_blocks(event.width)
        self._width = event.width

    def update_view(self, search: tuple = None, cur_page: int = -1) -> None:
        '''
        Get books and update books table. Search sets:
        (search val, column name), (0, "bookmark"), (0, "duplicates")
        '''
        # Request books if no pages
        if cur_page < 0:
            self.root.request_books(search=search)
            cur_page = 0
        # Clear books table
        table_children = self._books_frame.winfo_children()
        for i in table_children:
            i.destroy()
        if not state.books:
            return
        # Define pages.
        len_, limit = len(state.books), config.img_view_limit
        pages = len_ // limit
        self._pages = pages if len_ % limit == 0 else pages + 1

        # Create page with books covers
        self._fill_books_page(cur_page)

        self._page = cur_page
        self._canvas.yview_moveto(0)
        state.sel_books = state.last_select = None
        self._show_paging_buttons()
        self._table_focus()

    def _fill_books_page(self, cur_page) -> None:
        '''
        Create page with books covers.
        '''
        limit = config.img_view_limit
        # Calculate number of columns and remainder for additional padding
        cols, pad, pad_ext, hl_border = self._calculate_columns(self._width)
        col = -1
        book_block_idx = 0
        start, end = (cur_page * limit, (cur_page + 1) * limit)
        self._book_blocks = []
        for idx, book in enumerate(state.books):
            if idx < start or idx >= end:
                continue
            if col == cols - 1:
                col = -1
            row = book_block_idx // cols
            col += 1
            book_block = Preview(self.root, self._books_frame,
                book=book, idx=(idx, book_block_idx),
                    bind_funcs=(self._select_books,
                    self.root.menu.books_edit))
            book_block.configure(highlightthickness=hl_border,
                highlightbackground=self._colors["bg_mid"])
            book_block.grid(row=row, column=col,
                padx=(pad_ext, pad) if col == 0 else pad, pady=pad)
            self._book_blocks.append(book_block)
            book_block_idx += 1

    def _arrange_book_blocks(self, width: int) -> None:
        '''
        Rearrange books blocks after window resizing.
        '''
        # Calculate number of columns and remainder for additional padding
        cols, pad, pad_ext, _ = self._calculate_columns(width)
        # Rearrange book blocks
        col = -1
        for i, book in enumerate(self._book_blocks):
            if col == cols - 1: # if las column - reset
                col = -1
            row = i // cols
            col += 1
            book.grid(row=row, column=col,
                padx=(pad_ext, pad) if col == 0 else pad, pady=pad)
        self._books_frame.update()
        self._canvas.yview_moveto(0)

    def _calculate_columns(self, width: [int, None]) -> tuple:
        '''
        Calculate columns for covers table.
        '''
        hl_border, scroll_w = 3, 6
        pad = (self._book_pad if self._book_pad
            else 10 + hl_border + int(scroll_w / 2))
        self._book_pad = pad
        cols = width // (config.thumb_size[0] + pad * 2) if width else 3
        rem = width % (config.thumb_size[0] + pad * 2) if width else 0
        pad_ext = int(rem / 2) if rem > 0 else 0  # additional padding if reminder
        return (cols, pad, pad_ext, hl_border)

    def _show_paging_buttons(self) -> None:
        '''
        Show paging buttons if more than one page.
        '''
        if self._pages > 1:
            self._buttons_frame.grid()
        else:
            self._buttons_frame.grid_remove()
        # Print pages info between paging buttons
        self._page_label.configure(text=' '.join(
            ["Page", str(self._page + 1), "of", str(self._pages)]))

    def _table_focus(self) -> None:
        '''
        Set focus to first book. Wait for parent frame init.
        '''
        if hasattr(self.root, "content_frame"):
            self._select_books()
            self.focus_set()
            return
        self.after(100, self._table_focus)

    def _clear_selected(self, last) -> None:
        '''
        Remove highlight of selected books.
        '''
        blocks = (x for x in self._book_blocks if x.idx[0] in last)
        for i in blocks:
            i.configure(highlightbackground=self._colors["bg_mid"])

    def _select_books(self, event: object = None) -> None:
        '''
        Highlight selected books, load selected books, update preview.
        None event used for switching selection to first book.
        '''
        add = bool(event and event.state == 20) # 20 is Control + Mouse1
        sel_book_idx, blk_idx = (event.widget.idx if event
            else self._book_blocks[0].idx)
        last = state.last_select if state.last_select else (0,)
        if add and sel_book_idx in last:
            return
        if add:
            last = ((*last, sel_book_idx))
        else:
            state.sel_books = []
            self._clear_selected(last)
            last = (sel_book_idx,)
        self._book_blocks[blk_idx].configure(
            highlightbackground=self._colors["select_bg"])

        book_id = state.books[sel_book_idx]["book_id"]
        book = self.root.db_funcs.get_book(id_=book_id)
        if book and book not in state.sel_books:
            state.sel_books.append(book)
        state.last_select = last
        self.root.update_side_preview()
        self.root.set_footer_text.left(book.file)
