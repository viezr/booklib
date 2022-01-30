'''
Book authors frame.
'''
import glob
import os
from sys import platform
import subprocess
from threading import Thread
import tkinter as tk
from tkinter import filedialog as fd

from app import config, state
from .sub1 import BookDetailsMulti, TagDetails, Settings
from .book_details import BookDetails
from .views import views_set


class Menu(tk.Menu):
    '''
    Book authors frame class.
    '''
    def __init__(self, root: object, container: object):
        self.root, self.container = root, container
        tk.Menu.__init__(self, self.container, tearoff = 0)
        self._colors = self.root.style.colors
        self.configure(bg=self._colors["bg"], fg=self._colors["fg"],
            activebackground = self._colors["select_bg"],
            activeforeground = self._colors["fg"], relief="flat")

        self._cur_view = state.app_settings["default_view"]
        self._book_edit_open = False

        # Public methods: switch_view, add_books_files, add_books_dir
        # Public methods: read_book, read_quit, books_edit, tag_edit, export
        # Public methods: copy_to_clipboard, delete_book, delete_tag

        self._fill()

    def _fill(self) -> None:
        '''
        Load widgets.
        '''
        menu_set = {
            "File": (
                ("Add books", self.add_books_files, "Ctrl-O"),
                ("Add from folder", self.add_books_dir, ""),
                ("Export books", self.export, ""),
                ("Export tag books to",
                    lambda: self.export(tag=state.sel_tag), ""),
                ("Export to PDF", lambda: self.export(pdf=True), ""),
                ("Exit", self.root.destroy, "Ctrl-Q")
            ),
            "Edit": (
                ("Copy book info", self.copy_to_clipboard, "Ctrl-C"),
                ("Edit book", self.books_edit, "Enter"),
                ("Edit tag", self.tag_edit, "Enter"),
                ("Delete book", self.delete_book, ""),
                ("Delete tag", self.delete_tag, "")
            ),
            "Settings": (
                ("Export library to CSV", self._export_dbase, ""),
                ("Clean library", self._clean_lib, ""),
                ("Switch view", self.switch_view, ""),
                ("Settings", self._settings, "")
            )
        }
        for key, values_ in menu_set.items():
            menu = tk.Menu(self, tearoff=0, bg=self._colors["bg"],
                fg=self._colors["fg"],
            activebackground = self._colors["select_bg"],
            activeforeground = self._colors["fg"])
            for name_, cmd, accl in values_:
                menu.add_command(label=name_, command=cmd, accelerator=accl)
                if name_ in ("Export to PDF", "Switch view"):
                    menu.add_separator()
            self.add_cascade(label=key, menu=menu)

    def _add_books(self, files: list) -> None:
        '''
        Main function for adding books files.
        Get books info and covers from files. Add books data to database.
        '''
        files_len = len(files)
        self.root.show_wait_frame(title_label_add="Adding books to library...")
        self.root.update()

        change_wait_progress = self.root.get_wait_progress_func(files_len)
        for idx, src_file in enumerate(files):
            change_wait_progress(idx)
            book_file_obj = self.root.fd_funcs.get_book_file_data(src_file)
            if book_file_obj:
                self.root.db_funcs.add_book(book_file_obj)
            if self.root.db_funcs.success:
                self.root.fd_funcs.copy_book_files(book_file_obj)

        # Clean temp files
        Thread(target=self.root.fd_funcs.clean_temp, args=()).start()

        self.root.wait_frame.withdraw()
        self.root.update_view()

    ###           ###
    ### File menu ###
    ###           ###

    def add_books_files(self, event: object = None) -> None:
        '''
        Add books files.
        '''
        files = fd.askopenfilenames(title = 'Choose books',
            initialdir=os.path.expanduser("~/"),
            filetypes = [( "Book files", ' '.join([*config.book_types]) )]
        )
        if not files:
            self.root.show_message.warning("No files")
            return
        self._add_books(files)

    def add_books_dir(self) -> None:
        '''
        Add books files from directory.
        '''
        folder = fd.askdirectory(title = "Choose directory with books",
            initialdir=os.path.expanduser("~/"))
        if not folder:
            self.root.show_message.warning("No files chosen")
            return
        folder = os.path.normpath(folder)

        pattern = ''.join([folder,"/**/*.*"])
        files_all = glob.iglob(pattern, recursive=True)
        files = []
        for file in files_all:
            if any(file.endswith(x[1:]) for x in config.book_types):
                files.append(os.path.abspath(file))
        self._add_books(files)

    def export(self, pdf: bool = False, tag: bool = False) -> None:
        '''
        Save or export to PDF selected books and books by tag.
        '''
        def get_attr(book: [dict, object], attr: str) -> str:
            '''
            Return book value based on type of book.
            '''
            return book[attr] if tag else getattr(book, attr)

        if tag:
            ttype = state.sel_tag.tag_type
            tag = getattr(state.sel_tag, '_'.join([ttype, "name"]))
            books = state.books
        elif state.sel_books:
            books = state.sel_books
        else:
            books = None
        if not books:
            self.root.show_message.info("Please select book first")
            return
        folder = fd.askdirectory(title = "Choose directory for export",
            initialdir=os.path.expanduser("~/"))
        if not folder:
            self.root.show_message.warning("No folder set")
            return

        files_len = len(books)
        self.root.show_wait_frame(title_label_add="Exporting books...")
        self.root.update()

        folder = os.path.join(folder, tag) if tag else os.path.normpath(folder)
        change_wait_progress = self.root.get_wait_progress_func(files_len)
        for idx, book in enumerate(books):
            change_wait_progress(idx)

            b_file = get_attr(book, "file")
            file = os.path.join(state.app_settings["lib_books"], b_file)
            if pdf and not file.endswith(".pdf"):
                self.root.fd_funcs.convert_book_to(file, out_path=folder)
            else:
                b_snum = get_attr(book, "series_num")
                out_file = (''.join([str(b_snum).rjust(3, "0"), "_", b_file])
                    if b_snum > 0 else b_file)
                self.root.fd_funcs.copy_book_to(file, folder, out_file)

        self.root.wait_frame.withdraw()

    ###           ###
    ### Edit menu ###
    ###           ###

    def copy_to_clipboard(self, event: object = None) -> None:
        '''
        Copy book title and authors to clipboard.
        '''
        if not state.sel_books:
            self.root.show_message.info("No books selected")
            return
        if not state.last_select:
            return
        sel = state.last_select
        book = state.books[sel[0]]
        text = ' - '.join([book["authors"], book["title"]])
        self.clipboard_clear()
        self.clipboard_append(text)
        self.root.show_message.success(' '.join([text, "added to clipboard"]))

    def books_edit(self, event: object = None) -> None:
        '''
        Open book details.
        '''
        if not state.sel_books:
            self.root.show_message.info("No books selected")
            return
        children = (x.winfo_name()[:12] for x in
            self.root.content_frame.books_frame.winfo_children())
        if "!bookdetails" in children:
            return
        if len(state.sel_books) < 2:
            BookDetails(self.root, self.root.content_frame.books_frame)
        else:
            BookDetailsMulti(self.root, self.root.content_frame.books_frame)

    def tag_edit(self, event: object = None) -> None:
        '''
        Open tag details.
        '''
        if not state.sel_tag or state.sel_tag.tag_type == "bookmark":
            self.root.show_message.info("No tag selected")
            return
        children = (x.winfo_name()[:11] for x in
            self.root.content_frame.side_frame.winfo_children())
        if "!tagdetails" in children:
            return
        TagDetails(self.root, self.root.content_frame.side_frame)

    def delete_book(self) -> None:
        '''
        Delete selected books.
        '''
        books = state.sel_books if state.sel_books else []
        if not books:
            self.root.show_message.info("Please select book first")
            return
        message = (
            ''.join(["Do you really want to delete book?\n",
            '"', books[0].title, '"']) if len(books) == 1 else
            ''.join(["Do you really want to delete ",
            str(len(books)), " books?"])
        )
        mbox = tk.messagebox.askyesno(title="Delete book?",
            message=message)
        if not mbox:
            return
        for book in books:
            self.root.db_funcs.del_item(book)
        self._clean_lib(silent=True)

        state.sel_books = state.last_select = None
        self.root.update_view() # Update books table
        self.root.show_message.success("Books deleted")

    def delete_tag(self) -> None:
        '''
        Delete tag.
        '''
        if state.sel_tag.tag_type == "category" and state.sel_tag.dbid == 1:
            self.root.show_message.warning(
                "Unable to delete this category. Used for new books.")
            return
        search = (state.sel_tag.dbid, state.sel_tag.tag_type)
        books_for_tag = self.root.db_funcs.get_books(search=search,
            tag_search=True)
        if books_for_tag:
            self.root.show_message.warning(
                "Unable to delete tag with assosiated books")
            return
        self.root.db_funcs.del_item(state.sel_tag)
        self.root.update_side_tags()
        self.root.show_message.success("Tag deleted")

    ###               ###
    ### Settings menu ###
    ###               ###

    def _settings(self) -> None:
        '''
        Open setting window.
        '''
        Settings(self.root, self)

    def _export_dbase(self):
        '''
        Export database to CSV file.
        '''
        new_file = fd.asksaveasfile(title = "Choose file...",
            initialdir=os.path.expanduser("~/"),
            filetypes = [( "CSV files", "*.csv")]
        )
        if not new_file:
            self.root.show_message.warning("No file choosen")
            return
        books = self.root.db_funcs.get_books()
        header_str = ";".join(books[0].keys())
        books_str = [";".join([str(bv) for bv in book.values()])
            for book in books]
        new_file.write("\n".join([header_str, *books_str]))
        new_file.close()
        self.root.show_message.success("Export successful")

    def _clean_lib(self, silent: bool = False) -> None:
        '''
        Clean library.
        Delete unlinked authorships, authors from database.
        Delete files not linked to books in database.
        '''
        files = self.root.db_funcs.get_files()
        if not files:
            return
        db_files = []
        for file_name in files:
            db_files.append(file_name["file"])
            db_files.append(file_name["cover"])
        Thread(target=self.root.fd_funcs.clean_lib_files,
            args=(db_files,)).start()
        self.root.db_funcs.del_authorships_null() # del autorships first
        self.root.db_funcs.del_authors_null()
        if not silent:
            self.root.show_message.success("Library clean complete")

    def switch_view(self) -> None:
        '''
        Switch view (books table - books shelf).
        '''
        self.root.content_frame.books_frame.destroy()
        self._cur_view = 1 if self._cur_view == 0 else 0
        new_books_frame = views_set[self._cur_view][1](self.root,
            self.root.content_frame)
        self.root.content_frame.books_frame = new_books_frame
        self.root.content_frame.books_frame.grid(row=0, column=1, sticky="NSWE")
        self.root.update_view = new_books_frame.update_view

    ###           ###
    ### Book menu ### (used only for top panel yet)
    ###           ###

    @staticmethod
    def read_book(event: object = None) -> None:
        '''
        Open book in default application.
        '''
        book = state.sel_books[0]
        if not book:
            return
        file = os.path.join(state.app_settings["lib_books"], book.file)
        Thread(target=read_th, args=(file,)).start()

    def read_quit(self) -> None:
        '''
        Open book in default application, and close application.
        '''
        self.read_book()
        self.root.destroy()

def read_th(file) -> None:
    '''
    Thread for read_book.
    '''
    if platform == "win32":
        os.startfile(file)
    else:
        opener = "open" if platform == "darwin" else "xdg-open"
        subprocess.Popen([opener, file])
