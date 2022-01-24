'''
Book model for SQLite
'''


class Authorship():
    '''
    Authorship model for database
    '''
    __tablename__ = "authorships"
    __primary_key__ = "authorship_id"
    __unique_key__ = None # if necessary append "UNIQUE" to key
    authorship_id = "INTEGER PRIMARY KEY NOT null"
    book_id = " ".join(["INTEGER REFERENCES category (book_id)",
        "ON DELETE CASCADE ON UPDATE CASCADE"])
    author_id = " ".join(["INTEGER REFERENCES category (author_id)",
        "ON DELETE CASCADE ON UPDATE CASCADE"])
    UNIQUE = "(book_id, author_id)"

    def __init__(self, **kwargs):
        '''
        Set object attributes as class key = init kwarg.
        '''
        for key, val in kwargs.items():
            if key in __class__.__dict__:
                setattr(self, key, val)
        self._dbid = self.authorship_id

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
        return ' '.join(["Authorship object dbid:", self.dbid,
            "linked to: Book dbid", self.book_id,
            "Author dbid", self.author_id])
