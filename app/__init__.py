'''
App init.
'''
import os
from sys import platform, exit as sys_exit
import json

from .modules.sqlite import Db
from .config import Config, State, Style


def app_init() -> None:
    '''
    Load database, app settings.
    At first run, show welcome window for initial settings,
    create new database in books library directory.
    '''
    settings_file = os.path.abspath(
        os.path.join("app", "config", "settings"))
    # Create settings file if not exists
    if not os.path.exists(settings_file):
        from .welcome import Welcome
        Welcome(settings_file, platform).mainloop()
    if not os.path.exists(settings_file):
        sys_exit()
    # Load app settings and base path from settings file
    state.platform = platform
    state.app_settings_file = settings_file
    with open(state.app_settings_file, encoding="utf-8") as file:
        state.app_settings = json.load(file)
    db_path = os.path.join(state.app_settings["lib_path"], config.db_filename)
    # Load database or create new
    if not os.path.exists(db_path):
        dbase = Db(db_path)
        init_database(dbase)
    else:
        dbase = Db(db_path)
    state.dbase = dbase

def init_database(dbase: object) -> None:
    '''
    Fill new database with tables and some categories.
    '''
    from .models import Book, Author, Authorship, Category, Series
    # Create tables
    for Model in (Book, Author, Authorship, Category, Series):
        dbase.create_table(Model)
    # Create some categories (tags)
    categories = ["new", "prog", "prog_python", "prog_javascript",
        "prog_c", "prog_sql", "comp", "comp_linux", "culture",
        "math", "classic", "adventure", "business", "psychology",
        "sci-fi","sci-fi_fantasy", "sci-fi_space", "sport"]
    for cat in categories:
        dbase.insert_model(Category(category_name=cat))
    dbase.commit()

config = Config()
state = State()
