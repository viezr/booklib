'''
Preview frame
'''
from os import path
from time import time
import tkinter as tk
from PIL import Image, ImageTk

from app import config, state


class Preview(tk.Frame):
    '''
    Preview frame class
    idx and bind_funcs used for book_shelf frame
    '''
    def __init__(self, root: object, container: object,
        book: [object, dict] = None, idx: tuple = None,
        bind_funcs: tuple = None):

        self.root, self.container = root, container
        tk.Frame.__init__(self, self.container)
        self._colors = self.root.style.colors
        self.configure(takefocus=0, bg=self._colors["bg"])

        self.idx = idx # Tuple (books index, book_blocks index)
        self._bind_funcs = bind_funcs # Tuple (button1 func, double click func)
        self._default_thumb = path.normpath(config.default_thumb)

        # Public methods: update_img, clear_cache
        self.update_img(book)

    def _get_thumb_img_path(self, book: [object, dict] = None) -> str:
        '''
        Return full path for thumbnail image for book.
        '''
        img_file = ((book["cover"] if isinstance(book, dict) else book.cover)
            if book else None)
        thumb_img = (path.join(state.app_settings["lib_thumbs"], img_file)
            if img_file else None)
        if not thumb_img or not path.exists(thumb_img):
            thumb_img = self._default_thumb
        return thumb_img

    def clear_cache_img(self, book: [object, dict] = None) -> None:
        '''
        Clear item in cache. Used if cover file changed.
        '''
        thumb_img = self._get_thumb_img_path(book)
        _load_image(thumb_img, delete=True)

    def update_img(self, book: [object, dict] = None) -> None:
        '''
        Update image in preview frame.
        '''
        self._preview_canvas=tk.Canvas(self, width=config.thumb_size[0],
            height=config.thumb_size[1], bd=0,
            relief="flat", bg=self._colors["bg_mid" if self.idx else "bg"],
            highlightthickness=0)
        self._preview_canvas.idx = self.idx # for binding
        self._preview_canvas.grid(row=1, column=0)

        thumb_img = self._get_thumb_img_path(book)
        tk_image = _load_image(thumb_img)
        cur_size = tk_image.width(), tk_image.height()
        pad = ((config.thumb_size[0] - cur_size[0]) / 2,
            (config.thumb_size[1] - cur_size[1]) / 2)

        self._preview_canvas.create_image(
            pad[0], pad[1], image=tk_image, anchor="nw")
        if thumb_img == self._default_thumb and book:
            self._draw_text(book)

        if self._bind_funcs:
            self._preview_canvas.bind("<Button-1>", self._bind_funcs[0])
            self._preview_canvas.bind("<Double-1>", self._bind_funcs[1])

    def _draw_text(self, book: [object, dict]) -> None:
        '''
        Draw text with title and authors on default thumbnails.
        '''
        title = book["title"] if isinstance(book, dict) else book.title
        title = title.split()
        new_title = []
        prev = ""
        for word in title:
            if len(prev) + len(word) < 16:
                if new_title:
                    new_title.pop()
                word = " ".join([prev, word]) if prev else word
            new_title.append(word)
            prev = word
        pos_x, pos_y = config.thumb_size[0] / 2 + 4, 8
        for idx, line in enumerate(new_title):
            self._preview_canvas.create_text(pos_x, pos_y + 20 * (idx + 1),
                text=line, fill="white", font=('Helvetica 12 bold'))
        if isinstance(book, dict):
            author = " ".join(reversed(
                book["authors"].split(",")[0].split()[:2]))
            self._preview_canvas.create_text(pos_x, config.thumb_size[1] - 60,
                text=author, fill="white", font=('Helvetica 12 bold'))


def _get_cache(maxsize = None) -> callable:
    '''
    Custom LRU Cache decorator.
    Created for remove certain item instead of clearing whole cache.
    Delete oldest item at maxsize. Renew time of recent requests.
    Decorator maxsize argument set cache limit. Default 20.
    Function delete argument for remove item from cache.
    '''
    maxsize = maxsize if maxsize else 20
    cache = {}
    def get_cache_actual(func) -> callable:
        def wrapper(arg: str, delete: bool = False) -> [object, None]:
            if not isinstance(arg, str):
                raise Exception("Wrong argument type. Expect string.")
            if delete and arg in cache:
                cache.pop(arg)
                return None
            if not arg in cache:
                if len(cache) == maxsize and cache:
                    old = min(cache, key=lambda x: cache.get(x)[1])
                    cache.pop(old)
                cache[arg] = [func(arg), time()]
            else:
                # renew time of requested item
                cache[arg][1] = time()
            return cache[arg][0]
        return wrapper
    return get_cache_actual

@_get_cache(maxsize=config.img_cache_max)
def _load_image(thumb_img: str, delete: bool = False) -> [object, None]:
    '''
    Caching, return Tkinter image
    '''
    return ImageTk.PhotoImage(image=Image.open(thumb_img))
