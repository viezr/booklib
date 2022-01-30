'''
Book authors frame
'''
import tkinter as tk
from tkinter import ttk

from app import config, state


class BookAuthors(tk.Toplevel):
    '''
    Book authors frame class
    '''
    def __init__(self, root: object, container: object):
        self.root, self.container = root, container
        tk.Toplevel.__init__(self, self.container)
        self.title(" - ".join([config.app_title, "Authors"]))
        self.root.center_child(self, (712, 472))
        self.attributes('-topmost', 'true')
        if state.platform != "win32":
            self.attributes('-type', 'dialog')
        self._colors = self.root.style.colors
        self.configure(padx=10, pady=10, bg=self._colors["bg"])
        self.bind("<Escape>", self._quit_window)

        self._book = state.sel_books[0]
        self._fields = ["last_name", "first_name", "patronymic"]
        self._authors = self._authorships = None
        self._author_fields = self._new_author_fields = None
        self._book_changes = {}
        self._col1_w = 14

        self._fill()

    def _fill(self) -> None:
        '''
        Load widgets
        '''
        self.columnconfigure(0, weight=1)

        self._authors_frame = tk.Frame(self, bg=self._colors["bg"])
        self._authors_frame.grid(row=0, column=0, pady=10)
        self._update_frames()

        quit_button = ttk.Button(self, text="Close",
            command=self._quit_window)
        quit_button.grid(row=1, column=0)

        self._popup_menu = tk.Menu(self.root, tearoff = 0,
            bg=self._colors["bg"], fg=self._colors["fg"],
            activebackground = self._colors["select_bg"],
            activeforeground = self._colors["fg"])
        self._popup_menu.bind("<Leave>", self._popup_leave)
        self.bind("<Tab>", self._popup_leave)
        self.bind("<Button-1>", self._popup_leave)

    def _update_frames(self) -> None:
        '''
        Generate widgets for each author + one for new author
        '''
        frame_children = self._authors_frame.winfo_children()
        if frame_children:
            for child in frame_children:
                child.destroy()

        for idx, val in enumerate(self._fields):
            label = ttk.Label(self._authors_frame,
                text=val.title().replace("_", " "), width=self._col1_w)
            label.grid(row=0, column=idx, padx=10, sticky="W")

        next_row = self._create_authors_fields()
        self._create_newauthor_field(next_row)

    def _create_authors_fields(self) -> int:
        '''
        Create authors fields.
        '''
        # Author tuples (author object, self._author_fields, authorship object)
        # self._author_fields - tuples (entry widget, entry variable)
        self._authorships = self.root.db_funcs.get_authorships(self._book.dbid)
        self._authors = []
        adx = idx = 0
        for adx, ash in enumerate(self._authorships):
            author = self.root.db_funcs.get_author(id_=ash.author_id)
            self._author_fields = []
            for idx, field in enumerate(self._fields):
                entry_var = tk.StringVar()
                entry = ttk.Entry(self._authors_frame, textvariable=entry_var,
                    width=self._col1_w, validate="key",
                    validatecommand=(self.register(self._val_name), '%P', adx)
                    if idx == 0 else None
                )
                entry.grid(row=1 + adx, column=idx, padx=10, sticky="W")
                entry_var.set(getattr(author, field))
                self._author_fields.append((entry, entry_var))
            upd_button = ttk.Button(self._authors_frame, text="Upd", width=6,
                command=(self.register(self._upd_author), adx))
            upd_button.grid(row=1 + adx, column=idx + 1, padx=5, pady=2)
            del_button = ttk.Button(self._authors_frame, text="Del", width=6,
                command=(self.register(self._del_author), adx),
                style="Bad.TButton")
            del_button.grid(row=1 + adx, column=idx + 2, padx=5, pady=2)
            self._authors.append((author, self._author_fields, ash))
        return adx

    def _create_newauthor_field(self, next_row: int) -> None:
        '''
        Create field for new author.
        '''
        # For new author, create tuples (entry widget, entry variable)
        self._new_author_fields = []
        idx = 0
        for idx, _ in enumerate(self._fields):
            new_entry_var = tk.StringVar()
            new_entry = ttk.Entry(self._authors_frame,
                textvariable=new_entry_var, width=self._col1_w, validate="key",
                validatecommand=(self.register(self._val_name), '%P')
                if idx == 0 else None
            )
            new_entry.grid(row=2 + next_row, column=idx, padx=10, sticky="W")
            new_entry_var.set("")
            self._new_author_fields.append((new_entry, new_entry_var))
        new_button = ttk.Button(self._authors_frame, text="Add", width=6,
            command=self._new_author)
        new_button.grid(row=2 + next_row, column=idx + 1, padx=5, pady=10)

    def _val_name(self, value, adx: int = None) -> True:
        '''
        Show popup with names from database for any field.
        This validation callback return only True.
        '''
        # Ignore first char because of sqlite LIKE operator behavior
        # for unicode characters
        if not value.isascii():
            value = value.replace("'", "")[1:]
        if adx:
            fields = self._authors[int(adx)][1]
        else:
            fields = self._new_author_fields
        authors = None
        if len(value) > 1:
            authors = self.root.db_funcs.get_authors_name(value.lower())
            self._popup(fields, authors)
        return True

    def _popup_leave(self, event: object = None) -> None:
        '''
        Close popup menu on some events.
        '''
        self._popup_menu.delete(0, tk.END)

    def _popup_focus(self, event: object = None) -> None:
        self._popup_menu.focus_set()

    def _popup(self, fields: list, authors: list) -> None:
        '''
        Load authors full name popup menu and show it.
        '''
        self._popup_menu.delete(0, tk.END)
        if not authors:
            return
        field = fields[0][0]
        wnd_h = field.winfo_height()
        wnd_x, wnd_y = field.winfo_rootx(), field.winfo_rooty()

        for idx, auth in enumerate(authors):
            self._popup_menu.add_radiobutton(label=auth.full_name(),
                command = self._popup_set_fields(fields, authors[idx]))
        try:
            self._popup_menu.tk_popup(wnd_x, wnd_y + wnd_h)
        finally:
            self._popup_menu.grab_release()
        field.focus_set()
        field.bind("<Down>", self._popup_focus)

    @staticmethod
    def _popup_set_fields(fields: list, author: object) -> callable:
        '''
        Return wrapper for seting author fields from popup choice.
        '''
        def wrapper() -> None:
            '''
            Set author fields from popup choice.
            '''
            # fields[index of name field, index of field variable]
            fields[0][1].set(author.last_name)
            fields[1][1].set(author.first_name)
            fields[2][1].set(author.patronymic)
        return wrapper

    def _new_author(self) -> None:
        '''
        If author exists set it to authorship for book
        else add new author and authorship for book.
        '''
        flds = self._new_author_fields
        l_name, f_name, p_name = (x[1].get() for x in flds)
        if not l_name.strip(): # Highlight if last or first name empty
            self.root.bad_entry(flds[0][0])
            return
        if not f_name.strip():
            self.root.bad_entry(flds[1][0])
            return

        author = self.root.db_funcs.get_author(
            first_name=f_name, last_name=l_name, patronymic=p_name)
        if author:
            author_id = author.dbid
        else:
            self.root.db_funcs.add_author(l_name=l_name, f_name=f_name,
                p_name=p_name)
            author_id = self.root.db_funcs.get_last_row()

        self.root.db_funcs.add_authorship(book_id=self._book.dbid,
            author_id=author_id)
        self._update_containers()

    def _upd_author(self, adx: int) -> None:
        '''
        Update author names
        adx is the index for author in authors list
        '''
        author, auth_fields, authorship = self._authors[int(adx)]
        changes = {}
        for idx, field in enumerate(auth_fields):
            new_value = field[1].get()
            new_value = None if new_value.lower() == "none" else new_value
            changes[self._fields[idx]] = new_value
        if changes:
            # Change author if exists
            db_author = self.root.db_funcs.get_author(**changes)
            if db_author:
                self.root.db_funcs.update_item(
                    authorship, {"author_id": db_author.dbid})
            else:
                self.root.db_funcs.update_item(author, changes)
            self._update_containers()

    def _del_author(self, adx: int) -> None:
        '''
        Delete author
        '''
        authorship = self._authors[int(adx)][2]
        self.root.db_funcs.del_item(authorship)
        self._update_containers()

    def _update_containers(self) -> None:
        '''
        Update authors fields in authors and book frames
        '''
        self._update_frames()
        self.container.update_authors_field()

    def _quit_window(self, event: object = None) -> None:
        '''
        Close window
        '''
        self._popup_menu.destroy()
        self.destroy()
