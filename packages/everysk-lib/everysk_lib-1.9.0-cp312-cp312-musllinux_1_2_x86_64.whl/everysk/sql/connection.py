###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from contextvars import ContextVar, Token
from os import getpid
from types import TracebackType
from typing import Literal

from psqlpy import Connection, ConnectionPool, QueryResult
from psqlpy import Transaction as _Transaction

from everysk.config import settings
from everysk.core.log import Logger

_CONNECTIONS: dict[str, ConnectionPool] = {}
log = Logger('everysk-lib-sql-query')


def _log(message: str, extra: dict | None = None) -> None:
    if settings.POSTGRESQL_LOG_QUERIES:
        log.debug(message, extra=extra)


class Transaction:
    ## Private attributes
    _connection: Connection
    _pool: ConnectionPool
    _token: Token
    _transaction: _Transaction

    ## Public attributes
    connection: ContextVar[_Transaction] = ContextVar('postgresql-psqlpy-transaction', default=None)

    def __init__(self, dsn: str | None = None) -> None:
        self._pool: ConnectionPool = get_pool(dsn=dsn)

    async def __aenter__(self) -> None:
        self._connection = await self._pool.connection()
        self._transaction = self._connection.transaction()
        await self._transaction.begin()
        self._token = self.connection.set(self._transaction)

        return self

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: TracebackType | None
    ) -> None:
        if exc_type is None:
            await self._transaction.commit()
        else:
            await self._transaction.rollback()

        self.connection.reset(self._token)
        self._connection.close()

        return False


def make_connection_dsn(
    host: str | None = None,
    port: int | None = None,
    user: str | None = None,
    password: str | None = None,
    database: str | None = None,
) -> str:
    """
    Create a PostgreSQL connection DSN from settings.
    Supports both TCP and Unix socket connections.
    If parameters are provided, they override the settings.
    """
    options: dict[str, str | int] = {
        'host': host or settings.POSTGRESQL_CONNECTION_HOST,
        'port': port or settings.POSTGRESQL_CONNECTION_PORT,
        'user': user or settings.POSTGRESQL_CONNECTION_USER,
        'password': password or settings.POSTGRESQL_CONNECTION_PASSWORD,
        'database': database or settings.POSTGRESQL_CONNECTION_DATABASE,
    }
    # Handle Unix socket connections
    if options['host'].startswith('/'):
        return 'postgresql:///{database}?host={host}&user={user}&password={password}'.format(**options)

    # Standard TCP connection
    return 'postgresql://{user}:{password}@{host}:{port}/{database}'.format(**options)


def get_pool(dsn: str | None = None) -> ConnectionPool:
    """
    Get a connection pool for the current process.
    This is necessary because connections cannot be shared between processes.
    """
    dsn = dsn or make_connection_dsn()
    key = f'{getpid()}:{hash(dsn)}'
    if key not in _CONNECTIONS:
        _CONNECTIONS[key] = ConnectionPool(dsn=dsn, max_db_pool_size=settings.POSTGRESQL_POOL_MAX_SIZE)
    return _CONNECTIONS[key]


async def execute(
    query: str,
    params: dict | None = None,
    return_type: Literal['dict', 'list'] = 'list',
    dsn: str | None = None,
    cls: type | None = None,
) -> list[dict] | list[object] | dict:
    """
    Execute a query and return the results.
    If return_type is a class, return a list of instances of that class.
    If return_type is a string, return a dictionary keyed by that string.
    Otherwise, return a list of dictionaries.

    Args:
        query (str): The SQL query to execute.
        params (dict | None, optional): The parameters to include in the query. Defaults to None.
        return_type (Literal['dict', 'list'], optional): The type of return value. Defaults to 'list'.
        dsn (str | None, optional): The DSN to use for the connection. Defaults to None.
        cls (type | None, optional): The class to map the results to. Defaults to None.
    """
    conn = Transaction.connection.get()
    if not conn:
        pool: ConnectionPool = get_pool(dsn=dsn)
        conn = await pool.connection()
        log_message = 'PostgreSQL query executed.'
    else:
        log_message = 'PostgreSQL query executed within transaction.'

    _log(log_message, extra={'labels': {'query': query, 'params': params}})
    result: QueryResult = await conn.execute(query, params)
    if not Transaction.connection.get():
        conn.close()

    if cls:
        result = result.as_class(cls)
        if return_type == 'dict':
            return {row[cls._primary_key]: row for row in result}

        return result

    return result.result()
