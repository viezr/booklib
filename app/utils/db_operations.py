'''
Database operations interface
'''
import datetime as dt

from app import state
from app.models import Book, Author, Authorship, Category, Series


class DbaseInterface():
    '''
    Class for database interface
    '''
    def __init__(self):
        self._db = state.dbase
        self._tag_classes = {"category": Category, "series": Series}
        self._success = False # Public for checking successful transaction

    @property
    def success(self) -> bool:
        '''
        Return current transaction status and reset it.
        '''
        status = self._success
        self._success = False
        return status

    ###              ###
    ### Book queries ###
    ###              ###

    def main_query(self, where: str = None, having: str = None) -> str:
        '''
        Create main query for books request
        '''
        query = " ".join([
            "SELECT",
                "books.book_id,",
                "books.title,",
                "group_concat(authors.last_name || '",
                    "' || authors.first_name, ', ')",
                    "AS authors,",
                "category_name AS category,",
                "books.bookmark,",
                "books.read_state,",
                "books.rating,",
                "books.time_created,",
                "books.pub_date,",
                "books.isbn,",
                "series_name AS series,",
                "books.series_num,",
                "books.cover,",
                "books.file,",
                "books.pages",
            "FROM books",
            "LEFT JOIN authorships ON authorships.book_id = books.book_id",
            "LEFT JOIN authors ON authorships.author_id = authors.author_id",
            "LEFT JOIN categories ON books.category = categories.category_id",
            "LEFT JOIN series ON books.series = series.series_id",
            where,
            "GROUP BY books.book_id",
            having,
            "ORDER BY books.time_created DESC;",
        ])
        return query

    def get_books(self, search: [None, tuple] = None,
        tag_search: bool = False) -> [list, None]:
        '''
        Main query to get books by search value or all
        '''
        # Get values for books query
        val, val_type = search if search else (None, None)

        # Get books
        where = having = ""
        if val_type == "duplicates":
            return self.books_duplicates()
        elif val_type == "bookmark":
            where = ''.join(["WHERE books.", val_type, " = 1"])
        elif tag_search:
            where = (''.join(["WHERE books.", val_type, " = ", str(val)])
                if val else "")
        elif val_type == "authors":
            having = "".join([
                "HAVING authors.last_name LIKE '%",
                str(val), "%'"])
        elif val_type:
            where = ''.join(
                ["WHERE lower(books.", val_type, ") LIKE '%",
                str(val), "%'" ])

        books = self._db.execute(self.main_query(where, having))
        if books:
            return books
        return None

    def get_book(self, title: str = None, id_: int = None) -> [dict, None]:
        '''
        Get book by title or id
        '''
        if id_:
            where = ''.join(["book_id = ", str(id_)])
        else:
            where = ''.join(["title = ", "'", str(title), "'"])
        book = self._db.select_model(Book, where=where)
        if book:
            return book[0]
        return None

    def add_book(self, file_data) -> None:
        '''
        Add multiple books
        '''
        self._success = False
        title, authors, date_, pages, book_file, cover_file = file_data
        # Add book to database
        time_created = str(dt.datetime.now(dt.timezone.utc))
        try:
            self._db.insert_model(Book(title=title, pages=pages,
                time_created=time_created, pub_date=date_,
                file=book_file, cover=cover_file, category=1))
        except Exception as err:
            self._db.rollback()
            return
        # Get added book id
        book_db_id = self.get_last_row()
        if not book_db_id:
            self._db.rollback()
            return
        # Add authors and authorships
        for i in authors:
            author = self.get_author(first_name=i[0], last_name=i[1])
            if not author:
                self._db.insert_model(Author(first_name=i[0], last_name=i[1]))
                author = self.get_author(first_name=i[0], last_name=i[1])
            try:
                self._db.insert_model(Authorship(book_id=book_db_id,
                    author_id=author.dbid))
            except:
                pass
        self._db.commit()
        self._success = True

    ###             ###
    ### Tag queries ###
    ###             ###

    def get_tag(self, tag_type: str, name_: str = None,
        id_: int = None) -> [dict, None]:
        '''
        Get category by title or id
        '''
        if id_:
            where = ''.join([tag_type, "_id = ", str(id_)])
        elif name_:
            where = ''.join([tag_type, "_name = ", "'", name_, "'"])
        else:
            where = None
        result = self._db.select_model(self._tag_classes[tag_type], where=where)
        if result and where:
            return result[0]
        else:
            return result
        return None

    def add_tag(self, name_, tag_type = None) -> None:
        '''
        Add new category (tag)
        '''
        self._success = False
        kwarg = {''.join([tag_type,"_name"]): name_}
        self._db.insert_model(self._tag_classes[tag_type](**kwarg))
        self._db.commit()
        self._success = True

    ###                 ###
    ### Authors queries ###
    ###                 ###

    def get_author(self, first_name: str = None, last_name: str = None,
        patronymic: str = None, id_: int = None) -> [list, None]:
        '''
        Get author by names
        '''
        pat_suffix = ([" AND ", "patronymic = ", "'", str(patronymic), "'"]
            if patronymic else "")
        if first_name and last_name:
            where = ''.join([
                    "first_name = ", "'", str(first_name), "'", " AND ",
                    "last_name = ", "'", str(last_name), "'", *pat_suffix])
        elif id_:
            where=''.join(["author_id = ", str(id_)])

        author = self._db.select_model(Author, where=where)
        if author:
            return author[0]
        return None

    def get_authors(self, book_id: int) -> [dict, None]:
        '''
        Get concatenated authors for book
        '''
        authors = self._db.execute(" ".join([
            "SELECT",
                "group_concat(",
                    "authors.first_name || ' ' || authors.last_name, ', ')",
                "AS authors",
            "FROM books",
            "LEFT JOIN authorships ON authorships.book_id = books.book_id",
            "LEFT JOIN authors ON authorships.author_id = authors.author_id",
            "WHERE books.book_id =", str(book_id), ";"
        ]))
        if authors:
            return authors[0]["authors"]
        return None

    def get_authors_name(self, val) -> [list, None]:
        '''
        Get names of authors
        '''
        result = self._db.select_model(Author, where=''.join([
                "last_name LIKE '%", str(val), "%'"]), limit=20)
        if result:
            return result
        return None

    def add_author(self, f_name: str, l_name: str, p_name: str = None) -> None:
        '''
        Add author
        '''
        self._db.insert_model(Author(
            first_name=f_name, last_name=l_name, patronymic=p_name))
        self._db.commit()

    ###                     ###
    ### Authorships queries ###
    ###                     ###

    def get_authorships(self, book_id: int) -> [list, None]:
        '''
        Get all authorships for book
        '''
        authorships = self._db.select_model(
            Authorship, where=''.join(["book_id = ", str(book_id)])
        )
        if authorships:
            return authorships
        return None

    def add_authorship(self, book_id: int, author_id: int) -> None:
        '''
        Add authorship for book
        '''
        self._db.insert_model(Authorship(book_id=book_id,
                author_id=author_id))
        self._db.commit()

    ###                        ###
    ### Clean database queries ###
    ###                        ###

    def del_series_null(self) -> None:
        '''
        Delete all series without books relation
        '''
        series = self._db.execute(" ".join([
            "DELETE FROM series WHERE series_id IN (",
            "SELECT s.series_id",
            "FROM series s",
            "LEFT JOIN books b ON b.series = s.series_id",
            "WHERE b.book_id is null",
            ");",
        ]))
        self._db.commit()

    def del_categories_null(self) -> None:
        '''
        Delete all categories without books relation
        '''
        categories = self._db.execute(" ".join([
            "DELETE FROM categories WHERE category_id IN (",
            "SELECT s.category_id",
            "FROM category s",
            "LEFT JOIN books b ON b.category = s.category_id",
            "WHERE b.book_id is null",
            ");",
        ]))
        self._db.commit()

    def del_authorships_null(self) -> None:
        '''
        Delete all authorships without books relation
        '''
        authorships = self._db.execute(" ".join([
            "DELETE FROM authorships WHERE authorship_id IN (",
            "SELECT a.authorship_id",
            "FROM authorships a",
            "LEFT JOIN books b ON b.book_id = a.book_id",
            "WHERE b.book_id is null);",
        ]))
        self._db.commit()

    def del_authors_null(self) -> None:
        '''
        Delete all authors without authorship relation
        '''
        authors = self._db.execute(" ".join([
            "DELETE FROM authors WHERE author_id IN (",
            "SELECT a.author_id",
            "FROM authors a",
            "LEFT JOIN authorships ash ON ash.author_id = a.author_id",
            "WHERE ash.authorship_id is null);",
        ]))
        self._db.commit()

    ###               ###
    ### Other queries ###
    ###               ###

    def books_duplicates(self) -> [list, None]:
        books = self._db.execute(" ".join([
            "SELECT",
                "a.book_id,",
                "a.title,",
                "'' AS authors,",
                "a.category,",
                "a.bookmark,",
                "a.read_state,",
                "a.rating,",
                "a.time_created,",
                "a.pub_date,",
                "a.isbn,",
                "a.series,",
                "a.series_num,",
                "a.cover,",
                "a.file,",
                "a.pages",
            "FROM books a",
            "JOIN (SELECT title, COUNT(*)",
            "FROM books",
            "GROUP BY title",
            "HAVING count(*) > 1 ) b",
            "ON a.title = b.title",
            "ORDER BY a.title;",
        ]))
        if books:
            return books
        return None

    def get_files(self) -> [list, None]:
        '''
        Get all file names for books
        '''
        result = self._db.execute(
            ''.join([
                "SELECT file, cover FROM books;"
            ])
        )
        if result:
            return result
        return None

    def get_last_row(self) -> [str, int]:
        '''
        Get last row id for multiple transactions
        depended on previous insert
        '''
        return self._db.last_row()

    def update_item(self, item, kwargs) -> None:
        '''
        Update by object
        '''
        self._db.update_model(item, **kwargs)
        self._db.commit()

    def del_item(self, item) -> None:
        '''
        Delete by object
        '''
        self._db.delete_model(item)
        self._db.commit()

    def _alter_table(self) -> None:
        '''
        Alter table for some modifications.
        '''
        self._db.execute("ALTER TABLE category RENAME TO categories;")
