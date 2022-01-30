'''
Root window.
'''
from os import path
import tkinter as tk

from app import config, Style, state
from .frames import Menu, TopPanel, Content, Footer, WaitProcess
from .utils.db_operations import DbaseInterface
from .utils.files_operations import FilesInterface
from .modules.clean_translit import clean_with_underscore


class Booklib(tk.Tk):
    '''
    Main GUI class.
    '''
    def __init__(self):
        tk.Tk.__init__(self, className=config.app_title)
        self.title(config.app_title)
        self.minsize(width=600, height=600)
        self.geometry("1200x800")
        self.style = Style(state.app_settings["style_color"], state.platform)
        self.configure(padx=8, background=self.style.colors["bg"])
        if state.platform == "win32":
            self.iconbitmap("booklib.ico")
        self._fill()

    def _fill(self) -> None:
        '''
        Load widgets.
        '''
        self.menu = Menu(self, self)
        self.config(menu=self.menu)
        self.bind("<Control-o>", self.menu.add_books_files)
        self.bind("<Control-c>", self.menu.copy_to_clipboard)
        self.bind("<Control-q>", lambda x: self.destroy())

        # Main frames
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.top_frame = TopPanel(self, self)
        self.top_frame.grid(row=0, column=0, pady=10, sticky="WE")

        self.content_frame = Content(self, self)
        self.content_frame.grid(row=1, column=0, sticky="NSWE")

        self.footer_frame = Footer(self, self)
        self.footer_frame.grid(row=2, column=0, sticky="WE")

        self.wait_frame = WaitProcess(self, self)
        self.wait_frame.withdraw() # Hide waiting frame. Show on demand.

        # Interfaces
        self.db_funcs = DbaseInterface()
        self.fd_funcs = FilesInterface()
        self.set_footer_text = self.footer_frame.set_text
        self.show_message = self.top_frame.info_frame.show_message
        self.update_side_tags = self.content_frame.side_frame.update_side_tags
        self.update_side_preview = (
            self.content_frame.side_frame.update_side_preview)
        self.update_view = self.content_frame.books_frame.update_view
        self.show_wait_frame = self.wait_frame.show
        self.get_wait_progress_func = self.wait_frame.get_progress_func

    def center_child(self, window: object, size: tuple) -> None:
        '''
        Interface. Set size and center position of child window.
        '''
        wnd_w, wnd_h = size
        root_geo = self.winfo_geometry().split("+")
        root_w, root_h, root_x, root_y = root_geo[0].split("x") + root_geo[1:]
        window.geometry(''.join([
            str(wnd_w), "x", str(wnd_h), "+",
            str( int(root_x) + int((int(root_w) - wnd_w) / 2) ), "+",
            str( int(root_y) + int((int(root_h) - wnd_h) / 2) )
        ]))

    def bad_entry(self, entry: object) -> None:
        '''
        Interface. Highlight entry at wrong value.
        '''
        entry.configure(style="Bad.TEntry")
        self.after(2000, lambda: entry.configure(style="TEntry")
            if entry.winfo_exists() else None)

    def request_books(self, search: [None, tuple] = None) -> None:
        '''
        Interface. Request books for updating books frames.
        '''
        # Get books - list of dicts
        if search:
            values_ = search[0].split() if search[0] else 0
            books_cont = []
            for value in values_:
                books = self.db_funcs.get_books(search=(value, search[1]))
                books_cont += books if books else []
            state.books = []
            for i in books_cont:
                if i not in state.books:
                    state.books.append(i)
        elif state.sel_tag:
            search = (state.sel_tag.dbid, state.sel_tag.tag_type)
            state.books = self.db_funcs.get_books(search=search,
                tag_search=True)
        else:
            state.books = self.db_funcs.get_books()

        if hasattr(self, "footer_frame"):
            self.set_footer_text.right(" ".join(
                ["Books:",str(len(state.books) if state.books else 0)]))
        if not state.books:
            self.show_message.info("No books found")
            return
        self.sort_books()

    def check_tag_name(self, value: str, tag_type: str) -> [str, None]:
        '''
        Interface. Check tag value for length and database conflict.
        '''
        # Change value to lowercase with underscores if tag is category
        new_value = (clean_with_underscore(value).lower()
            if tag_type == "category" else value)
        if len(new_value) < 2:
            self.show_message.warning("Tag name is too short")
            return None
        if self.db_funcs.get_tag(tag_type=tag_type, name_=new_value):
            self.show_message.warning(''.join(
                ["Tag ", "'", new_value,"'", " exists"]))
            return None
        return new_value

    @staticmethod
    def sort_books() -> None:
        '''
        Interface. Sort books.
        '''
        if not state.books:
            return
        db_column, direction = state.last_sort
        state.books = sorted(state.books,
            key=lambda x: x[db_column] if not x[db_column] is None else "",
            reverse=direction)
