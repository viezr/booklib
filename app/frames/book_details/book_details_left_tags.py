'''
Book details frame.
'''
import tkinter as tk
from tkinter import ttk

from app import state


class BookDetailsLeftTags(tk.Frame):
    '''
    Book details frame class.
    '''
    def __init__(self, root: object, container: object):
        self.root, self.container = root, container
        tk.Frame.__init__(self, self.container)
        self.configure(bg=self.root.style.colors["bg"])
        self.columnconfigure(0, weight=1)

        # Public methods: update_authors_field only for authors frame

        self._tags_combo_frames = []
        self._book_changes = {}
        self._book = self.container.book
        self._ser_num_var = tk.StringVar()
        self._ser_num_entry = None

        self._fill()

    def _fill(self) -> None:
        '''
        Load widgets.
        '''
        frames_set = (("category", "categories"), ("series", "series"))
        idx = 0
        for idx, (tag_type, state_tags_type) in enumerate(frames_set):
            frame = tk.Frame(self, bg=self.root.style.colors["bg"])
            frame.grid(row=idx, column=0, sticky="W", pady=(0, 12))

            ttk.Label(frame, text=tag_type.title(), width=15).grid(
                row=idx, column=0)
            tag_combo_values, tags_id_list, current_tag = self._combo_settings(
                tag_type, state_tags_type)
            tag_combo = ttk.Combobox(frame, values=tag_combo_values,
                exportselection=0, width=20)
            tag_combo.grid(row=idx, column=1)
            if current_tag >= 0:
                tag_combo.current(current_tag)
            self._create_series_num_field(frame, idx)
            self._tags_combo_frames.append((tag_combo, tags_id_list, tag_type))

    def _combo_settings(self, tag_type: str, state_tags_type: str) -> None:
        '''
        Set some settings for tag combobox field.
        '''
        tag_combo_values = []
        tags_id_list = []
        current_tag = -1
        state_tags = getattr(state, state_tags_type)
        book_tag_id = getattr(self._book, tag_type)
        if state_tags:
            for tdx, tag in enumerate(state_tags):
                tag_combo_values.append(tag.db_name)
                tags_id_list.append(tag.dbid)
                if tag.dbid == book_tag_id:
                    current_tag = tdx
        return (tag_combo_values, tags_id_list, current_tag)

    def _create_series_num_field(self, frame: object, idx: int) -> None:
        '''
        Add field with number of current book in series.
        '''
        if idx != 1:
            return
        ttk.Label(frame, text="Num in series",
            width=11 if state.platform != "win32" else 13).grid(
            row=idx, column=2, padx=(24, 4), sticky="W")
        self._ser_num_entry = ttk.Entry(frame,
            textvariable=self._ser_num_var, width=4)
        self._ser_num_var.set(self._book.series_num)
        self._ser_num_entry.grid(row=idx, column=3, sticky="W")

    def _update_check_series_num(self) -> bool:
        '''
        Check number of series field changes for book update.
        '''
        ser_num = self._ser_num_var.get()
        try:
            ser_num = int(ser_num)
            if ser_num not in range(1000):
                raise ValueError
        except ValueError:
            self.root.bad_entry(self._ser_num_entry)
            return False

        if not self._book.series_num == ser_num:
            self._book_changes["series_num"] = ser_num
        return True

    def _update_check_tags(self) -> bool:
        '''
        Check tag fields and set changes for book update.
        '''
        for frame in self._tags_combo_frames:
            combo, tags_id_list, tag_type = frame
            current_tag_idx, tag_name = combo.current(), combo.get()
            book_tag_id = getattr(self._book, tag_type)
            if not tag_name:
                if book_tag_id:
                    self._book_changes[tag_type] = ""
                continue
            state_tag_id = (tags_id_list[current_tag_idx]
                if current_tag_idx >= 0 else None)
            if current_tag_idx < 0: # If new tag
                new_tag_name = self.root.check_tag_name(tag_name, tag_type)
                if not new_tag_name:
                    return False
                new_tag_dbid = self._add_new_tag(new_tag_name, tag_type)
                if new_tag_dbid:
                    self._book_changes[tag_type] = (new_tag_dbid)
            elif state_tag_id and not book_tag_id == state_tag_id:
                self._book_changes[tag_type] = state_tag_id
        return True

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

    def get_updated_fields(self) -> [dict, None]:
        '''
        Return fields changes or None.
        '''
        # Check changes series number and tag fields.
        self._book_changes = {} # Clear changes
        if not all((self._update_check_series_num(), self._update_check_tags())):
            return None

        return self._book_changes
