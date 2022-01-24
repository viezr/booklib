'''
Sidebar frame.
'''
import tkinter as tk
from tkinter import ttk

from app import state
from app.models import Bookmark
from app.frames.sub2 import Preview, Cover, MenuPopup


class Side(tk.Frame):
    '''
    Sidebar frame class.
    '''
    def __init__(self, root: object, container: object):
        self.root, self.container = root, container
        tk.Frame.__init__(self, self.container)
        self.rowconfigure(0, weight=1)
        self._colors = self.root.style.colors
        self.configure(bg=self._colors["bg"])
        self.columnconfigure(0, weight=1)

        self._preview_frame = None
        self._cover_window = None
        # [(Frame tree, Tag type for db, state var name for tags list),]
        self._tree_blocks = []

        # public methods: update_side_tags, update_side_preview

        self._frames_fill()
        self._wait_interface()

    def _wait_interface(self) -> None:
        if not hasattr(self.root, "db_funcs"):
            self.after(50, self._wait_interface)
        else:
            self.update_side_tags()

    def _frames_fill(self) -> None:
        '''
        Load tags widgets.
        '''
        frames_set = (("category", "categories"), ("series", "series"))
        # Frame
        frame = tk.Frame(self, bg=self._colors["bg"])
        frame.grid(row=0, column=0, sticky="NWSE")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        for idx, fset in enumerate(frames_set):
            # Treeview
            ytags_scroll = ttk.Scrollbar(frame, orient="vertical",
                style="Vertical.TScrollbar")
            ytags_scroll.grid(row=idx, column=1, sticky="NSE")
            tree_widget = ttk.Treeview(frame, selectmode="browse",
                yscrollcommand=ytags_scroll.set, style="Side.Treeview")
            tree_widget.tag_configure("odd", background=self._colors["bg"])
            tree_widget.tag_configure("even",
                background=self._colors["treeview_side_bg2"])
            ytags_scroll.config(command=tree_widget.yview)
            tree_widget.heading("#0", text=fset[0].title(), anchor="center")
            tree_widget.column("#0", anchor="w", width=60)

            tree_widget.bind("<<TreeviewSelect>>", self._tag_selected(idx))
            tree_widget.grid(row = idx, column = 0, sticky = "NSWE")
            tree_widget.bind("<ButtonRelease-3>", self._popup_menu)
            tree_widget.bind("<FocusIn>", self._table_focus(tree_widget))

            self._tree_blocks.append((tree_widget, fset[0], fset[1]))

        ttk.Button(self, text="All", command=self._show_all, takefocus=0,
            width=6).grid(row=1, column=0, pady=8, padx=(0, 8), sticky="W")
        ttk.Button(self, text="Bookmarks", command=self._show_bookmarks,
            takefocus=0, width=10).grid(row=1, column=0, pady=8, padx=(0, 8),
            sticky="E")

        self._preview_frame=Preview(self.root, self)
        self._preview_frame.grid(row=2, column=0, padx=(0, 8))

        self._preview_frame.bind("<Enter>", self._show_cover)
        self._preview_frame.bind("<Leave>", self._show_cover)

    def update_side_tags(self) -> None:
        '''
        Update tags in this frame.
        '''
        for i in self._tree_blocks:
            self._frames_update(i)

    def update_side_preview(self) -> None:
        '''
        Update preview in frame.
        '''
        if state.sel_books:
            self._preview_frame.update_img(state.sel_books[0])

    def _popup_menu(self, event: object = None) -> None:
        '''
        Show popup menu on mouse right click.
        '''
        MenuPopup(self.root, self, tag=True)

    def _frames_update(self, tree_block: tuple) -> None:
        '''
        Update list of tags.
        '''
        tree_widget, tag_type, state_attr = tree_block
        table_children = tree_widget.get_children()
        if table_children:
            tree_widget.delete(*table_children)
        # get tags list of objects
        tags = self.root.db_funcs.get_tag(tag_type=tag_type)
        # update state tags
        setattr(state, state_attr, tags)
        if not tags:
            return
        for i, item in enumerate(tags):
            tree_widget.insert(parent='', index="end", iid=i,
                text=item.db_name, tags=("even" if i % 2 == 0 else "odd",))

    def _show_cover(self, event: object) -> None:
        '''
        Show big cover.
        '''
        if not state.sel_books:
            return
        if int(event.type.value) == 7: # Enter
            self._cover_window = Cover(self.root, self, state.sel_books[0])
        else: # Leave
            self._cover_window.destroy()

    def _show_all(self) -> None:
        '''
        Show all books.
        '''
        state.sel_books = state.last_select = None
        state.sel_tag = None
        self.root.update_view()

    def _show_bookmarks(self) -> None:
        '''
        Show bookmarks.
        '''
        state.sel_books = state.last_select = None
        state.sel_tag = Bookmark()
        self.root.update_view()

    @staticmethod
    def _table_focus(tree_widget: object = None) -> None:
        '''
        Return wrapper for setting focus to certain tag.
        '''
        def wrapper(event: object = None):
            '''
            Set focus to certain tag.
            '''
            nonlocal tree_widget
            sel = tree_widget.selection()
            children = tree_widget.get_children()
            if sel:
                sel = sel[0]
            elif children:
                sel = children[0]
                tree_widget.selection_set(sel) # move selection
            else:
                return
            tree_widget.focus(sel) # move focus
            tree_widget.see(sel) # scroll to show it
        return wrapper

    @staticmethod
    def _get_selection(tree_widget: object) -> tuple:
        '''
        Convert selection iid's from strings to integer.
        '''
        return int(tree_widget.selection()[0] if tree_widget.selection() else 0)

    def _tag_selected(self, idx: int) -> callable:
        '''
        Return wrapper for update books list by selected tag.
        '''
        def wrapper(event: object = None) -> None:
            '''
            Update books list by selected tag.
            '''
            widget, _, state_attr = self._tree_blocks[idx]
            selection = self._get_selection(widget)
            sel_tag = getattr(state, state_attr)[selection]
            if state.sel_tag == sel_tag:
                return
            state.sel_books = state.last_select = None
            if state_attr == "series":
                state.last_sort = ("series_num", 0)
            state.sel_tag = sel_tag
            self.root.update_view()
        return wrapper
