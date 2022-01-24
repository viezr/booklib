'''
App states
'''


class State():
    '''
    States class
    '''
    def __init__(self):
        self.dbase = None # Database object
        self.app_settings = None # app settings loaded from file
        self.app_settings_file = None
        self.books = [] # List of dicts - books from database
        self.sel_books = [] # selected books - Book objects
        self.last_select = tuple() # tuple of last selected indexes of books
        self.last_sort = ("title", 0) # (sor column in table view, direction)
        self.sel_tag = None # Category or Seires object
        self.paltform = None

    def __repr__(self):
        '''
        Object description
        '''
        return ''.join(["<", self.__module__, ".State",
            " Application states object>"])

    def __str__(self):
        '''
        Return application settings
        '''
        return ''.join(["Application settings:", self.app_settings])
