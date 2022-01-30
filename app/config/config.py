'''
App config
'''
from dataclasses import dataclass


@dataclass
class Config():
    '''
    Main app config class
    '''
    app_title = "Booklib"
    db_filename: str = "booklib.db"
    max_cover_size: tuple = (1080, 1920)
    thumb_size: tuple = (192, 256) # thumbnails size
    default_thumb: str = "app/static/sample_cover.png"
    img_view_limit: int = 32
    img_cache_max: int = img_view_limit * 4
    book_types: tuple = ("*.pdf", "*.epub", "*.fb2", "*.fb2.zip", "*.djvu",
        "*.azw", "*.azw3", "*.mobi", "*.txt", "*.chm")

    # Columns for treeview (db_name, column name, width)
    # Order depends on database query columns order
    columns: tuple = (
        ("book_id", "Book id", 50), ("title", "Title", 300),
        ("authors", "Authors", 100), ("category", "Tag", 100),
        ("bookmark", "*", 20), ("read_state", "Read", 44),
        ("rating", "Rate", 40), ("time_created", "Created",60),
        ("pub_date", "Pub year",60), ("isbn", "ISBN",60),
        ("series", "Series",60), ("series_num", "Ser #", 40),
        ("cover", "Cover", 20), ("file", "File", 20)
    )
