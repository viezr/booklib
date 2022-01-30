'''
Book file model for storing book file data.
'''


class BookFile():
    '''
    Book file class.
    '''
    def __init__(self, src_file: str, date: [object, None], pages: int):
        self.src_file = src_file
        self.title = None
        self.authors = None
        self.pub_date = date
        self.pages = pages
        self.book_file_name = None
        self.cover_file_name = None

    def __repr__(self):
        '''
        Object description
        '''
        return ''.join(["<", self.__module__, ".BookFile",
            " Book file object>"])

    def __str__(self):
        '''
        Return Book file attributes
        '''
        return ' '.join(["Book file attributes", self.__dict__])
