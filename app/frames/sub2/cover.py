'''
Full cover view window
'''
from os import path
import tkinter as tk
from PIL import Image, ImageTk

from app import config, state


class Cover(tk.Toplevel):
    '''
    Full cover frame class
    '''
    def __init__(self, root: object, container: object,
        book: [object, dict, None] = None):

        self.root, self.container = root, container
        tk.Toplevel.__init__(self, self.container)
        self.title(" - ".join([config.app_title, "Processing..."]))
        self._im_size = (600, 800)
        self._set_position()
        self.attributes('-topmost', 'true')
        if state.platform != "win32":
            self.attributes('-type', 'dialog')
        self._colors = self.root.style.colors
        self.configure(bg=self._colors["bg"])

        self._default_thumb = path.normpath(config.default_thumb)

        self._fill(book)

    def _set_position(self) -> None:
        '''
        Set size and position of window
        '''
        wnd_w, wnd_h = self._im_size[0] + 40, self._im_size[1] + 40
        root_geo = self.root.winfo_geometry().split("+")
        _, root_h, root_x, root_y = root_geo[0].split("x") + root_geo[1:]
        self.geometry(''.join([
            str(wnd_w), "x", str(wnd_h), "+",
            str( int(root_x) + 220 ), "+",
            str( int(root_y) + int((int(root_h) - wnd_h) / 2) )
        ]))

    def _fill(self, book: [object, dict, None]) -> None:
        '''
        Show full cover
        '''
        img_file = ((book["cover"] if isinstance(book, dict) else book.cover)
            if book else None)
        thumb_img = (path.join(state.app_settings["lib_covers"], img_file)
            if img_file else self._default_thumb)

        img = Image.open(thumb_img)
        img.thumbnail((self._im_size[0], self._im_size[1]))
        self.tk_image = ImageTk.PhotoImage(image=img)

        cur_size = self.tk_image.width(), self.tk_image.height()
        pad = (self._im_size[0] - cur_size[0]) / 2, (self._im_size[1] - cur_size[1]) / 2
        self._preview_canvas=tk.Canvas(self, width=self._im_size[0],
            height=self._im_size[1], bd=0,
            relief="flat", bg=self._colors["bg"], highlightthickness=0)
        self._preview_canvas.create_image(
            pad[0], pad[1], image=self.tk_image, anchor="nw")
        self._preview_canvas.grid(row=1, column=0, padx=20, pady=20)
