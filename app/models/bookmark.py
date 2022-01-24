'''
Model for bookmark tag
'''


class Bookmark():
    '''
    Bookmark model as additional tag with _id attribute
    '''
    def __init__(self):
        self._dbid = 0
        self._tag_type = "bookmark"

    @property
    def dbid(self):
        '''
        Return database id.
        '''
        return self._dbid

    @property
    def tag_type(self):
        '''
        Return tag type.
        '''
        return self._tag_type
