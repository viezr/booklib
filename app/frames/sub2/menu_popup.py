'''
Book authors frame
'''
import tkinter as tk


class MenuPopup(tk.Menu):
    '''
    Book authors frame class
    '''
    def __init__(self, root: object, container: object, tag: bool = False):
        self.root, self.container = root, container
        tk.Menu.__init__(self, self.container, tearoff = 0)
        self._colors = self.root.style.colors
        self.configure(bg=self._colors["bg"], fg=self._colors["fg"],
            activebackground = self._colors["select_bg"],
            activeforeground = self._colors["fg"])
        self.bind("<Leave>", lambda x: self.destroy())

        self._tag = tag
        self._fill()

    def _fill(self) -> None:
        '''
        Load widgets
        '''
        menu = self.root.menu
        edit_func = (menu.tag_edit if self._tag else menu.books_edit)
        delete_func = (menu.delete_tag if self._tag else menu.delete_book)
        items_ = (("Edit", edit_func),
            ("Save to", lambda: menu.export(tag=self._tag)),
            ("Export to PDF", lambda: menu.export(pdf=True, tag=self._tag)),
            ("Delete", delete_func))
        for i in items_:
            self.add_radiobutton(label=i[0], command = i[1])
        try:
            self.tk_popup(
                self.root.winfo_pointerx() - 10, self.root.winfo_pointery() - 10)
        finally:
            self.grab_release()
