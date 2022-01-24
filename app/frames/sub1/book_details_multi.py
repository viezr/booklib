'''
Book details frame.
'''
import tkinter as tk
from tkinter import ttk

from app import state


class BookDetailsMulti(tk.Toplevel):
    '''
    Book details frame class.
    '''
    def __init__(self, root: object, container: object):
        self.root, self.container = root, container
        tk.Toplevel.__init__(self, self.container)
        self.title(" - ".join([self.root.wtitle, "Multiple edit"]))
        self.root.center_child(self, (448, 240))
        self.attributes('-topmost', 'true')
        if state.platform != "win32":
            self.attributes('-type', 'dialog')
        self._colors = self.root.style.colors
        self.configure(padx=10, pady=4, bg=self._colors["bg"])
        self.bind("<Escape>", self._quit_window)

        self._book_changes = {}
        self._tags_combo_frames = []
        self._rating_var = tk.IntVar()
        self._rating_vars = []


        self._fill()

    def _fill(self) -> None:
        '''
        Load widgets.
        '''
        self.columnconfigure(0, weight=1)

        self._tag_frames_field() # 0,1 rows inside

        self._rating_frame = tk.Frame(self, bg=self._colors["bg"])
        self._rating_frame.grid(row=2, column=0, pady=10, sticky="W")
        self._rating_field()

        bottom_frame = tk.Frame(self, bg=self._colors["bg"])
        bottom_frame.grid(row=3, column=0, pady=10)
        btn_funcs = (("Update", self._update_book),
            ("Close", self._quit_window))
        for i, func in enumerate(btn_funcs):
            button = ttk.Button(bottom_frame, text=func[0],
                command=func[1])
            button.grid(row=1, column=i, padx=20, pady=(10, 0))

    def _tag_frames_field(self) -> None:
        '''
        Category (tag) field.
        '''
        def combo_settings(state_tags_type: str) -> tuple:
            '''
            Set some settings for tag combobox field.
            '''
            tag_combo_values = []
            tags_id_list = []
            state_tags = getattr(state, state_tags_type)
            if state_tags:
                for tag in state_tags:
                    tag_combo_values.append(tag.db_name)
                    tags_id_list.append(tag.dbid)
            return (tag_combo_values, tags_id_list)

        frames_set = (("category", "categories"), ("series", "series"))
        for idx, (book_tag_type, state_tags_type) in enumerate(frames_set):
            frame = tk.Frame(self, bg=self._colors["bg"])
            frame.grid(row=idx, column=0, pady=10, sticky="W")

            label = ttk.Label(frame, text=book_tag_type.title(),
                width=15)
            label.grid(row=idx, column=0)

            tag_combo_values, tags_id_list = combo_settings(state_tags_type)
            tag_combo = ttk.Combobox(frame, values=tag_combo_values,
                exportselection=0)
            tag_combo.grid(row=idx, column=1)
            self._tags_combo_frames.append(
                (tag_combo, tags_id_list, book_tag_type))

    def _rating_field(self) -> None:
        '''
        Rating field.
        '''
        ttk.Label(self._rating_frame, text="Rating", width=15).grid(row=0, column=0)

        val_frame = tk.Frame(self._rating_frame, bg=self.root.style.colors["bg"])
        val_frame.grid(row=0, column=1)
        for val in range(5):
            rt_var = tk.IntVar()
            ttk.Checkbutton(val_frame, variable=rt_var,
                command=self._set_rating(val + 1), takefocus=False,
                style="Rating.TCheckbutton").grid(row=0, column=val)
            self._rating_vars.append(rt_var)

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

    def _update_check_tags(self) -> None:
        '''
        Check tag fields changes for book update.
        '''
        for frame in self._tags_combo_frames:
            combo, tags_id_list, tag_type = frame
            current_tag_idx, tag_name = combo.current(), combo.get()
            state_tag_id = (tags_id_list[current_tag_idx]
                if current_tag_idx >= 0 else None)
            if not tag_name:
                continue
            if current_tag_idx < 0: # New category
                new_tag_name = self.root.check_tag_name(tag_name, tag_type)
                if not new_tag_name:
                    continue
                new_tag_dbid = self._add_new_tag(new_tag_name, tag_type)
                if new_tag_dbid:
                    self._book_changes[tag_type] = (new_tag_dbid)
            elif state_tag_id:
                self._book_changes[tag_type] = state_tag_id

    def _add_new_tag(self, tag_name: str, tag_type: str) -> int:
        '''
        Add new tag, return new tag database id.
        '''
        tag_dbid = 0
        self.root.db_funcs.add_tag(tag_name, tag_type=tag_type)
        if self.root.db_funcs.success:
            tag_dbid = self.root.db_funcs.get_last_row()
            self.root.update_side_tags()
        return tag_dbid

    def _update_book(self) -> None:
        '''
        Update book data by changed fields.
        Check fileds and set changes in self._book_changes dict.
        '''
        # Check tag changes. If changed, update it in database.
        self._update_check_tags()

        # Check rating changes
        rating = self._rating_var.get()
        if rating != 0:
            self._book_changes["rating"] = rating

        if not self._book_changes:
            return

        # Update book details in database from self._book_changes
        for book in state.sel_books:
            self.root.db_funcs.update_item(book, self._book_changes)
        # clear selected book to renew selected book object
        state.sel_books = state.last_select = None
        self.root.show_message.success("Books updated")
        self.root.update_view()
        self.destroy() # Close window

    def _quit_window(self, event: object = None) -> None:
        '''
        Close window
        '''
        self.destroy()
