'''
Book model for SQLite
'''


class Category():
    '''
    Category model for database
    '''
    __tablename__ = "categories"
    __primary_key__ = "category_id"
    __unique_key__ = None # if necessary append "UNIQUE" to key
    category_id = "INTEGER PRIMARY KEY NOT null"
    category_name = "TEXT NOT null"

    def __init__(self, **kwargs):
        '''
        Set object attributes as class key = init kwarg.
        '''
        for key, val in kwargs.items():
            if key in __class__.__dict__:
                setattr(self, key, val)
        self._dbid = self.category_id
        self._db_name = self.category_name
        self._tag_type = "category"

    @property
    def dbid(self):
        '''
        Return database id.
        '''
        return self._dbid

    @property
    def db_name(self):
        '''
        Return tag name.
        '''
        return self._db_name

    @property
    def tag_type(self):
        '''
        Return tag type.
        '''
        return self._tag_type
