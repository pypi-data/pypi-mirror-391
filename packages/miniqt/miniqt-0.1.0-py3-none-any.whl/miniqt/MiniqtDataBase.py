import dataset
from dataset.database import Database, safe_reraise
from dataset.table import Table
from dataset.util import row_type
from minibt.indicators import IndicatorClass, pd, np, os, Union, Optional
from minibt.utils import datetime
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class MiniqtDataBase:
    """数据库默认路径./minibt/miniqt/MiniqtDataBase.db

    所有数据全部以列表形式保存和获取，数据库表格的第一行，有多少个数据就有多少列
    >>> get_value(self, table_name: str, id=1) -> list:获取数据
        set_value(self, table_name: str, values: list, id=1) -> list:保存数据

        Opens a new connection to a database.

        *url* can be any valid `SQLAlchemy engine URL`_.  If *url* is not defined
        it will try to use *DATABASE_URL* from environment variable.  Returns an
        instance of :py:class:`Database <dataset.Database>`. Additionally,
        *engine_kwargs* will be directly passed to SQLAlchemy, e.g. set
        *engine_kwargs={'pool_recycle': 3600}* will avoid `DB connection timeout`_.
        Set *row_type* to an alternate dict-like class to change the type of
        container rows are stored in.::

            db = dataset.connect('sqlite:///factbook.db')

        One of the main features of `dataset` is to automatically create tables and
        columns as data is inserted. This behaviour can optionally be disabled via
        the `ensure_schema` argument. It can also be overridden in a lot of the
        data manipulation methods using the `ensure` flag.

        If you want to run custom SQLite pragmas on database connect, you can add them
        to on_connect_statements as a set of strings. You can view a full
        `list of PRAGMAs here`_.

        .. _SQLAlchemy Engine URL: http://docs.sqlalchemy.org/en/latest/core/engines.html#sqlalchemy.create_engine
        .. _DB connection timeout: http://docs.sqlalchemy.org/en/latest/core/pooling.html#setting-pool-recycle
        .. _list of PRAGMAs here: https://www.sqlite.org/pragma.html"""
    defalut_url = os.path.join(BASE_DIR, "MiniqtDataBase.db")

    def __init__(self, url=None,
                 schema=None,
                 engine_kwargs=None,
                 ensure_schema=True,
                 row_type=row_type,
                 sqlite_wal_mode=True,
                 on_connect_statements=None,
                 ):
        self._db_dir = f'sqlite:///{url if url else self.defalut_url}'
        try:
            self._db: Database = dataset.connect(
                self._db_dir, schema, engine_kwargs, ensure_schema, row_type, sqlite_wal_mode, on_connect_statements)
        except:
            self._db: Database = dataset.connect(
                f'sqlite:///{self.defalut_url}', schema, engine_kwargs, ensure_schema, row_type, sqlite_wal_mode, on_connect_statements)

    @property
    def isupdate(self) -> Optional[bool]:
        now_date = datetime.now().date()
        date = self.get_value("isupdate")
        if not date:
            self.create_table("isupdate")
            self.table("isupdate").upsert(dict(id=1, date=now_date), ["id"])
            return True
        if date[0] != now_date:
            self.table("isupdate").upsert(dict(id=1, date=now_date), ["id"])
            return True

    def get_value(self, table_name: str, id=1) -> list:
        if not self.has_table(table_name):
            return []
        table = self.table(table_name)
        if len(table.columns) <= 1:
            return []
        return list(next(table.find(id=id)).values())[1:]

    def set_value(self, table_name: str, values: list, id=1) -> list:
        if values:
            self.drop(table_name)
            table = self.table(table_name)
            data = {str(i): value for i, value in enumerate(values)}
            data.update(dict(id=id))
            table.upsert(data, ["id"])

    @property
    def db(self):
        return self._db

    def has_table(self, table_name):
        return self._db.has_table(table_name)

    def exists(self, table_name: str):
        """Check to see if the table currently exists in the database."""
        return self.table(table_name).exists

    def create_table(self, table_name, primary_id=None, primary_type=None, primary_increment=None):
        """Create a new table.

        Either loads a table or creates it if it doesn't exist yet. You can
        define the name and type of the primary key field, if a new table is to
        be created. The default is to create an auto-incrementing integer,
        ``id``. You can also set the primary key to be a string or big integer.
        The caller will be responsible for the uniqueness of ``primary_id`` if
        it is defined as a text type. You can disable auto-increment behaviour
        for numeric primary keys by setting `primary_increment` to `False`.

        Returns a :py:class:`Table <dataset.Table>` instance.
        ::

            table = db.create_table('population')

            # custom id and type
            table2 = db.create_table('population2', 'age')
            table3 = db.create_table('population3',
                                     primary_id='city',
                                     primary_type=db.types.text)
            # custom length of String
            table4 = db.create_table('population4',
                                     primary_id='city',
                                     primary_type=db.types.string(25))
            # no primary key
            table5 = db.create_table('population5',
                                     primary_id=False)
        """
        if table_name in self.tables:
            return self.tables(table_name)
        return self._db.create_table(table_name, primary_id, primary_type, primary_increment)

    def load_table(self, table_name):
        """Load a table.

        This will fail if the tables does not already exist in the database. If
        the table exists, its columns will be reflected and are available on
        the :py:class:`Table <dataset.Table>` object.

        Returns a :py:class:`Table <dataset.Table>` instance.
        ::

            table = db.load_table('population')
        """
        return self._db.load_table(table_name)

    def get_table(
        self,
        table_name,
        primary_id=None,
        primary_type=None,
        primary_increment=None,
    ):
        """Load or create a table.

        This is now the same as ``create_table``.
        ::

            table = db.get_table('population')
            # you can also use the short-hand syntax:
            table = db['population']
        """
        return self._db.get_table(table_name, primary_id, primary_type, primary_increment)

    def query(self, query, *args, **kwargs):
        """Run a statement on the database directly.

        Allows for the execution of arbitrary read/write queries. A query can
        either be a plain text string, or a `SQLAlchemy expression
        <http://docs.sqlalchemy.org/en/latest/core/tutorial.html#selecting>`_.
        If a plain string is passed in, it will be converted to an expression
        automatically.

        Further positional and keyword arguments will be used for parameter
        binding. To include a positional argument in your query, use question
        marks in the query (i.e. ``SELECT * FROM tbl WHERE a = ?``). For
        keyword arguments, use a bind parameter (i.e. ``SELECT * FROM tbl
        WHERE a = :foo``).
        ::

            statement = 'SELECT user, COUNT(*) c FROM photos GROUP BY user'
            for row in db.query(statement):
                print(row['user'], row['c'])

        The returned iterator will yield each result sequentially.
        """
        return self._db.query(query, *args, **kwargs)

    @property
    def tables(self):
        """Get a listing of all tables that exist in the database."""
        return self._db.tables

    def table(self, table_name: str) -> Table:
        """Get a reference to the table, which may be reflected or created."""
        if not self.has_table(table_name):
            self.create_table(table_name)
        return self._db[table_name]

    def columns(self, table_name: str):
        """Get a listing of all columns that exist in the table."""
        return self.table(table_name).columns

    def has_column(self, table_name: str, column):
        """Check if a column with the given name exists on this table."""
        return self.table(table_name).has_column(column)

    def find(self, table_name: str, *_clauses, limit=None, offset=0, order_by=None, streamed=False, step=1000):
        """Perform a simple search on the table.

        Simply pass keyword arguments as ``filter``.
        ::

            results = table.find(country='France')
            results = table.find(country='France', year=1980)

        Using ``_limit``::

            # just return the first 10 rows
            results = table.find(country='France', _limit=10)

        You can sort the results by single or multiple columns. Append a minus
        sign to the column name for descending order::

            # sort results by a column 'year'
            results = table.find(country='France', order_by='year')
            # return all rows sorted by multiple columns (descending by year)
            results = table.find(order_by=['country', '-year'])

        You can also submit filters based on criteria other than equality,
        see :ref:`advanced_filters` for details.

        To run more complex queries with JOINs, or to perform GROUP BY-style
        aggregation, you can also use :py:meth:`db.query() <dataset.Database.query>`
        to run raw SQL queries instead.
        """
        kwargs = dict(_limit=limit, _offset=offset,
                      order_by=order_by, _streamed=streamed, _step=step)
        return self.table(table_name).find(*_clauses, **kwargs)

    def insert(self, table_name, row, ensure=None, types=None):
        """Add a ``row`` dict by inserting it into the table.

        If ``ensure`` is set, any of the keys of the row are not
        table columns, they will be created automatically.

        During column creation, ``types`` will be checked for a key
        matching the name of a column to be created, and the given
        SQLAlchemy column type will be used. Otherwise, the type is
        guessed from the row value, defaulting to a simple unicode
        field.
        ::

            data = dict(title='I am a banana!')
            table.insert(data)

        Returns the inserted row's primary key.
        """
        return self.table(table_name).insert(row, ensure, types)

    def insert_ignore(self, table_name, row, keys, ensure=None, types=None):
        """Add a ``row`` dict into the table if the row does not exist.

        If rows with matching ``keys`` exist no change is made.

        Setting ``ensure`` results in automatically creating missing columns,
        i.e., keys of the row are not table columns.

        During column creation, ``types`` will be checked for a key
        matching the name of a column to be created, and the given
        SQLAlchemy column type will be used. Otherwise, the type is
        guessed from the row value, defaulting to a simple unicode
        field.
        ::

            data = dict(id=10, title='I am a banana!')
            table.insert_ignore(data, ['id'])
        """
        return self.table(table_name).insert_ignore(row, keys, ensure, types)

    def insert_many(self, table_name, rows, chunk_size=1000, ensure=None, types=None):
        """Add many rows at a time.

        This is significantly faster than adding them one by one. Per default
        the rows are processed in chunks of 1000 per commit, unless you specify
        a different ``chunk_size``.

        See :py:meth:`insert() <dataset.Table.insert>` for details on
        the other parameters.
        ::

            rows = [dict(name='Dolly')] * 10000
            table.insert_many(rows)
        """
        # Sync table before inputting rows.
        return self.table(table_name).insert_many(rows, chunk_size, ensure, types)

    def update(self, table_name, row, keys, ensure=None, types=None, return_count=False):
        """Update a row in the table.

        The update is managed via the set of column names stated in ``keys``:
        they will be used as filters for the data to be updated, using the
        values in ``row``.
        ::

            # update all entries with id matching 10, setting their title
            # columns
            data = dict(id=10, title='I am a banana!')
            table.update(data, ['id'])

        If keys in ``row`` update columns not present in the table, they will
        be created based on the settings of ``ensure`` and ``types``, matching
        the behavior of :py:meth:`insert() <dataset.Table.insert>`.
        """
        return self.table(table_name).update(row, keys, ensure, types, return_count)

    def update_many(self, table_name, rows, keys, chunk_size=1000, ensure=None, types=None):
        """Update many rows in the table at a time.

        This is significantly faster than updating them one by one. Per default
        the rows are processed in chunks of 1000 per commit, unless you specify
        a different ``chunk_size``.

        See :py:meth:`update() <dataset.Table.update>` for details on
        the other parameters.
        """
        return self.table(table_name).update_many(rows, keys, chunk_size, ensure, types)

    def upsert(self, table_name, row, keys, ensure=None, types=None):
        """An UPSERT is a smart combination of insert and update.

        If rows with matching ``keys`` exist they will be updated, otherwise a
        new row is inserted in the table.
        ::

            data = dict(id=10, title='I am a banana!')
            table.upsert(data, ['id'])
        """
        return self.table(table_name).upsert(row, keys, ensure, types)

    def upsert_many(self, table_name, rows, keys, chunk_size=1000, ensure=None, types=None):
        """
        Sorts multiple input rows into upserts and inserts. Inserts are passed
        to insert and upserts are updated.

        See :py:meth:`upsert() <dataset.Table.upsert>` and
        :py:meth:`insert_many() <dataset.Table.insert_many>`.
        """
        # Removing a bulk implementation in 5e09aba401. Doing this one by one
        # is incredibly slow, but doesn't run into issues with column creation.
        return self.table(table_name).update_many(rows, keys, chunk_size, ensure, types)

    def delete(self, table_name: str, *clauses, **filters):
        """Delete rows from the table.

        Keyword arguments can be used to add column-based filters. The filter
        criterion will always be equality:
        ::

            table.delete(place='Berlin')

        If no arguments are given, all records are deleted.
        """
        return self.table(table_name).delete(*clauses, **filters)

    def import_from_csv(self, table_name: str, path: str):
        return self.table(table_name).import_from_csv(path)

    def export_to_csv(self, table_name: str, path: str):
        return self.table(table_name).export_to_csv(path)

    def create_column(self, table_name: str, name, type, **kwargs):
        """Create a new column ``name`` of a specified type.
        ::

            table.create_column('created_at', db.types.datetime)

        `type` corresponds to an SQLAlchemy type as described by
        `dataset.db.Types`. Additional keyword arguments are passed
        to the constructor of `Column`, so that default values, and
        options like `nullable` and `unique` can be set.
        ::

            table.create_column('key', unique=True, nullable=False)
            table.create_column('food', default='banana')
        """
        return self.table(table_name).create_column(name, type, **kwargs)

    def create_column_by_example(self, table_name: str, key, value):
        """
        Explicitly create a new column ``name`` with a type that is appropriate
        to store the given example ``value``.  The type is guessed in the same
        way as for the insert method with ``ensure=True``.
        ::

            table.create_column_by_example('length', 4.2)

        If a column of the same name already exists, no action is taken, even
        if it is not of the type we would have created.
        """
        return self.table(table_name).create_column_by_example(key, value)

    def find_one(self, table_name: str, *args, offset=0, order_by=None, streamed=False):
        """Get a single result from the table.

        Works just like :py:meth:`find() <dataset.Table.find>` but returns one
        result, or ``None``.
        ::

            row = table.find_one(country='United States')
        """
        kwargs = dict(_limit=1, _offset=offset,
                      order_by=order_by, _streamed=streamed, _step=None)
        return self.table(table_name).find_one(*args, **kwargs)

    def drop(self, table_name: str):
        """Drop the table from the database.

        Deletes both the schema and all the contents within it.
        """
        if self.has_table(table_name):
            return self.table(table_name).drop()

    def drop_column(self, table_name: str, column: Union[str, list[str]]):
        """
        Drop the column ``name``.
        ::

            table.drop_column('created_at')

        """
        if isinstance(column, str):
            column = [column,]
        for col in column:
            self.table(table_name).drop_column(col)

    def to_dataframe(self, table_name, *_clauses, limit=None, offset=0, order_by=None, streamed=False, step=1000):
        return pd.DataFrame(self.find(table_name, *_clauses, limit=limit, offset=offset, order_by=order_by, streamed=streamed, step=step))

    def count(self, table_name: str, *_clauses, **kwargs):
        """Return the count of results for the given filter set."""
        return self.table(table_name).count(*_clauses, **kwargs)

    def distinct(self, table_name: str, *args, **_filter):
        """Return all the unique (distinct) values for the given ``columns``.
        ::

            # returns only one row per year, ignoring the rest
            table.distinct('year')
            # works with multiple columns, too
            table.distinct('year', 'country')
            # you can also combine this with a filter
            table.distinct('year', country='China')
        """
        return self.table(table_name).distinct(*args, **_filter)

    def close(self):
        try:
            self._db.close()
            del self._db
        except:
            ...

    def __enter__(self):
        """Start a transaction."""
        self._db.begin()
        return self

    def __exit__(self, error_type, error_value, traceback):
        """End a transaction by committing or rolling back."""
        if error_type is None:
            try:
                self._db.commit()
            except Exception:
                with safe_reraise():
                    self._db.rollback()
        else:
            self._db.rollback()
