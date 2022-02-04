'''
Files operations module.
'''
import os
import shutil
from tempfile import mkdtemp, gettempdir
from threading import Thread
from secrets import token_hex
from PIL import Image, ImageTk

from app import config, state
from app.models import BookFile
from app.modules.clean_translit import clean_with_underscore, clean_with_space
from app.modules.clean_translit import chars_to_ascii
from app.modules.mupdf import get_book_info, get_cover_img, convert_to_pdf
from app.modules.unzip_fb2 import unzip_fb2


class FilesInterface():
    '''
    Interface for file operations.
    '''
    def __init__(self):
        self._settings = state.app_settings
        self._tmp_prefix: str = "booklib_" # prefix for temp directories

    @staticmethod
    def convert_book_to(file: str, out_path: str) -> None:
        '''
        Convert book and save to given path.
        '''
        convert_to_pdf(file, out_path)

    @staticmethod
    def copy_book_to(file: str, out_path: str, out_file: str) -> None:
        '''
        Copy book file to direcotry.
        '''
        if not os.path.exists(out_path):
            os.mkdir(out_path)
        dst = os.path.join(out_path, out_file)
        shutil.copy2(file, dst)

    def clean_temp(self) -> None:
        '''
        Clean temp files
        '''
        dirs = os.scandir(gettempdir())
        for dir_ in dirs:
            if dir_.name.startswith(self._tmp_prefix):
                shutil.rmtree(dir_.path, ignore_errors=True)

    def change_cover_file(self, src_file: str, book_file_name: str) -> None:
        '''
        Change book cover image
        '''
        self._copy_cover_file(src_file, book_file_name)

    def clean_lib_files(self, db_files: list) -> None:
        '''
        Clean library files not linked to database files.
        '''
        paths = (self._settings[x] for x in
            ["lib_books", "lib_covers", "lib_thumbs"])
        os_scan, os_stat, os_remove = os.scandir, os.stat, os.remove
        for path in paths:
            files = os_scan(path)
            for file in files:
                size = os_stat(file.path).st_size
                if not file.name in db_files or size == 0:
                    os_remove(file.path)

    def get_book_file_data(self, src_file: str) -> [object, None]:
        '''
        Parse files for metadata, return book file object.
        '''
        src_file = os.path.normpath(src_file)
        file_name = os.path.split(src_file)[1]

        # Uncompress fb2.zip
        if src_file.endswith(".fb2.zip"):
            tmp_file = unzip_fb2(src_file, prefix=self._tmp_prefix)
            src_file = tmp_file if tmp_file else src_file

        # Get book info from meta data
        meta_title = meta_authors = date = None
        pages = 0
        if any(src_file.endswith(x) for x in (".pdf", ".epub", ".fb2")):
            meta_title, meta_authors, date, pages = get_book_info(src_file)
        # Get book info from file name
        if not all([meta_title, meta_authors]):
            file_title, file_authors = self._get_info_from_file(file_name)

        book_filename = self._check_rename_filename(file_name)
        cover_filename = ''.join([os.path.splitext(book_filename)[0], ".png" ])

        book_file = BookFile(src_file, date, pages)
        book_file.title = meta_title if meta_title else file_title
        book_file.authors = meta_authors if meta_authors else file_authors
        book_file.book_file_name = book_filename
        book_file.cover_file_name = cover_filename

        return book_file

    @staticmethod
    def _get_info_from_file(file_name: str) -> list:
        '''
        Get book info from file name.
        '''
        # authors should be list of authors [[name1, name2],...]
        file_title = None
        title_author = os.path.splitext(file_name)[0]
        if "-" in title_author:
            file_authors, file_title = title_author.split("-", 1)
            file_title = clean_with_space(file_title) # clean title
            file_authors = clean_with_space(file_authors)
            file_authors = file_authors.split(" ", 1) # clean + list
            if len(file_authors) == 1: # if list [name1,] add none item for name2
                file_authors.append("Unknown")
            file_authors = [file_authors,]
        else: # if no divider
            file_title = clean_with_space(title_author.strip()) # clean title
            file_authors = [["Unknown", "Unknown"],] # make list
        return (file_title, file_authors)

    def _check_rename_filename(self, file_name: str) -> str:
        '''
        If same file exists in library, add suffix and return new name.
        '''
        file_name = chars_to_ascii(clean_with_underscore(file_name)).lower()
        dst_file = os.path.join(self._settings["lib_books"], file_name)
        if os.path.exists(dst_file):
            file, ext = os.path.splitext(file_name)
            file_name = ''.join([file, "_",token_hex(4), ext])
        return file_name

    def copy_book_files(self, book_file: object) -> None:
        '''
        Copy book file and cover to library
        '''
        self._copy_book_file(book_file)
        # Get cover from book file
        cover_tmp = get_cover_img(
            book_file.src_file, max_size=config.max_cover_size,
            prefix=self._tmp_prefix)
        # Copy cover file and make thumbnail
        self._copy_cover_file(cover_tmp, book_file.cover_file_name)

    def _copy_book_file(self, book_file: object) -> None:
        '''
        Copy book files to library.
        '''
        dst_file = os.path.join(self._settings["lib_books"],
            book_file.book_file_name)
        shutil.copy2(book_file.src_file, dst_file)

    def _copy_cover_file(self, src_file: str, new_cover_file: str) -> None:
        '''
        Copy cover file and created thumbnail to library.
        '''
        if not src_file:
            return
        # Convert cover to png if it has other extension
        if os.path.splitext(src_file)[-1] != ".png":
            src_file = self._convert_cover(src_file)
            if not src_file:
                return
        dst_cover = os.path.join(self._settings["lib_covers"], new_cover_file)
        shutil.copy2(src_file, dst_cover)
        self._make_thumbnail(src_file, new_cover_file)

    def _convert_cover(self, src_file: str) -> str:
        '''
        Convert covers to png format
        '''
        tmp_path = os.path.normpath(mkdtemp(prefix=self._tmp_prefix))
        new_cover_file = os.path.join(tmp_path, "book_cover.png")
        try:
            with Image.open(src_file) as im:
                if not im.mode == "RGB":
                    im = im.convert("RGB")
                im.save(new_cover_file)
        except:
            return None
        return new_cover_file

    def _make_thumbnail(self, src_file: str, new_cover_file: str) -> None:
        '''
        Create thumbnail image
        '''
        try:
            thumb_img = os.path.join(self._settings["lib_thumbs"],
                new_cover_file)
            with Image.open(src_file) as im:
                if not im.mode == "RGB":
                    im = im.convert("RGB")
                im.thumbnail(config.thumb_size)
                im.save(thumb_img)
        except:
            pass
