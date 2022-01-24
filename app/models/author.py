'''
Author model for SQLite
'''


class Author():
    '''
    Author model for database
    '''
    __tablename__ = "authors"
    __primary_key__ = "author_id"
    __unique_key__ = None # if necessary append "UNIQUE" to key
    author_id = "INTEGER PRIMARY KEY NOT null"
    first_name = "TEXT NOT null"
    last_name = "TEXT NOT null"
    patronymic = "TEXT DEFAULT null"
    UNIQUE = "(first_name, last_name)"

    def __init__(self, **kwargs):
        '''
        Set object attributes as class key = kwarg value.
        '''
        for key, val in kwargs.items():
            if key in __class__.__dict__:
                setattr(self, key, val)
        self._dbid = self.author_id

    @property
    def dbid(self):
        '''
        Return database id.
        '''
        return self._dbid

    def full_name(self) -> str:
        '''
        Return author full name
        '''
        full_name = (x for x in (self.last_name, self.first_name,
            self.patronymic) if x)
        return ' '.join(full_name)

    def __str__(self) -> str:
        '''
        Return string with author instance id and full name
        '''
        return ' '.join(["Author", "dbid:", str(self.dbid), "name:",
            self.last_name, self.first_name, str(self.patronymic)])
