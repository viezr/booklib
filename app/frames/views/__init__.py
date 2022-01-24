'''
Subframes module 1
'''
from .books_table import BooksTable
from .books_shelf import BooksShelf

views_set = (("Table view", BooksTable), ("Covers view", BooksShelf))
