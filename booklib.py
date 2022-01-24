#!/usr/bin/env python3
'''
Books library application
'''
from app import app_init
from app.app_root import Booklib


if __name__ == "__main__":
    app_init()
    Booklib().mainloop()
