# Booklib
E-books manager written in Python.  
![image](screenshot.gif)  

I desided to write this app because I'd like to have a fast book manager
with minimum and necessary features.  
Despite it being written in Python, the app is working pretty fast and
using only two external libraries - Pillow and PyMuPDF.  

## Features
- Store all library files in one place (database file, books, covers and
thumbnails) so the library can be easily moved.
- Add multiple book files or directory with book files.
While adding books to library, metadata and cover extracted from pdf, epub
and fb2. If metadata can't be extracted, author and title are set from file name.
- Save or export (to pdf) selected book outside of the library.
- Save or export (to pdf) books by tag or series outside of the library.
If exported series, the app saves books to series name directory with
series number prefix for each book.
- Search books by title, authors etc. Search duplicates.
- Sort books by columns in table view.
- Switch view of books (table or covers).
- Show zoomed cover by moving mouse on the bottom-left preview image.
- Show books by category, series, bookmarks.
- Context search for authors in author's "last name" field.
- Some settings: columns to show in table view, default view,
interface colors ("dark", "light"), open other (new) library.
- Export database to CSV format (";" delimiter).

## Some shortcuts:
- Ctrl-C - copy book title and author to clipboard.
- Ctrl-O - add books to the library.
- Ctrl-Q - quit Booklib.
- Enter - open book details.
- Ctrl-Enter - open book in default application.
- Esc - close window.

## Notes
At first run (or after selecting "Open library" in settings) show a welcome
window for setting library directory.  
Read function opens book in default system application.  
For author names used separate fields to prevent mess with order and
delimiters.  
In menu options, "Clean library" remove unused authorships, authors from
the database, and files from library folder not associated to books in
the database.

## Install
There aren't any binaries as all in one for installation and runnung,
but it only needs Python and Python's pip packages - Pillow and PyMuPDF.  
Python 3.8.10 - 3.10.1 versions should be OK, other versions have not been
tested.  
Change the main file "booklib.py" extension to ".pyw" to run in Windows
without Python's console.  
To show icon in Windows taskbar instead of Python's icon, create a shortcut
with path: `"C:\<path to pythonw.exe>" "C:\<path to booklib.py>"`, and change
the shortcut icon.
