'''
Book model for SQLite
'''


class Book():
    '''
    Book model for database
    '''
    __tablename__ = "books"
    __primary_key__ = "book_id"
    __unique_key__ = None # if necessary append "UNIQUE" to key
    book_id = "INTEGER PRIMARY KEY NOT null"
    title = "TEXT NOT null"
    pages = "INTEGER DEFAULT 0"
    read_state = "INTEGER DEFAULT 0"
    rating = "INTEGER DEFAULT 0"
    bookmark = "INTEGER DEFAULT 0"
    series_num = "INTEGER DEFAULT 0"
    time_created = "TEXT NOT null"
    pub_date = "TEXT"
    isbn = "TEXT"
    file = "TEXT NOT null"
    cover = "TEXT"
    category = " ".join(["INTEGER REFERENCES category (category_id)",
        "ON DELETE CASCADE ON UPDATE CASCADE"])
    series = " ".join(["INTEGER REFERENCES category (series_id)",
        "ON DELETE CASCADE ON UPDATE CASCADE"])

    def __init__(self, **kwargs):
        '''
        Set object attributes as class key = init kwarg.
        '''
        for key, val in kwargs.items():
            if key in __class__.__dict__:
                setattr(self, key, val)
        self._dbid = self.book_id

    @property
    def dbid(self):
        '''
        Return database id.
        '''
        return self._dbid

    def __str__(self):
        '''
        Return string with object description.
        '''
        return ' '.join(["Book object dbid:", self.dbid, "Title", self.title,])
