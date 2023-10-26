from typing import Optional, Callable

from redblue.commands import Commands
from redblue.connection import ConnectionPool


class RedBlue(Commands):
    def __init__(
            self,
            host="localhost",
            port=7379,
            master_port=7379
    ) -> None:
        """
        Initialize a new Redis client.
        To specify a retry policy for specific errors, first set
        `retry_on_error` to a list of the error/s to retry on, then set
        `retry` to a valid `Retry` object.
        To retry on TimeoutError, `retry_on_timeout` can also be set to `True`.

        Args:

        single_connection_client:
            if `True`, connection pool is not used. In that case `Redis`
            instance use is not thread safe.
        """
        self.connection_pool = ConnectionPool(host=host, port=port)
        self.connection = self.connection_pool.get_connection("_")

        self.master_conn_pool = ConnectionPool(host=host, port=master_port)
        self.master_conn = self.master_conn_pool.get_connection("-")

    def __repr__(self) -> str:
        return f"{type(self).__name__}<{repr(self.connection_pool)}>"

    def get_encoder(self) -> "Encoder":
        """Get the connection pool's encoder"""
        return self.connection_pool.get_encoder()

    def get_connection_kwargs(self) -> dict:
        """Get the connection's key-word arguments"""
        return self.connection_pool.connection_kwargs

    def get_retry(self) -> Optional["Retry"]:
        return self.get_connection_kwargs().get("retry")

    def set_retry(self, retry: "Retry") -> None:
        self.get_connection_kwargs().update({"retry": retry})
        self.connection_pool.set_retry(retry)

    def load_external_module(self, funcname, func) -> None:
        """
        This function can be used to add externally defined redis modules,
        and their namespaces to the redis client.

        funcname - A string containing the name of the function to create
        func - The function, being added to this class.

        ex: Assume that one has a custom redis module named foomod that
        creates command named 'foo.dothing' and 'foo.anotherthing' in redis.
        To load function functions into this namespace:

        from redis import Redis
        from foomodule import F
        r = Redis()
        r.load_external_module("foo", F)
        r.foo().dothing('your', 'arguments')

        For a concrete example see the reimport of the redisjson module in
        tests/test_connection.py::test_loading_external_modules
        """
        setattr(self, funcname, func)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __del__(self):
        self.close()

    def close(self):
        # In case a connection property does not yet exist
        # (due to a crash earlier in the Redis() constructor), return
        # immediately as there is nothing to clean-up.
        if not hasattr(self, "connection"):
            return

        conn = self.connection
        if conn:
            self.connection = None
            self.connection_pool.release(conn)

            self.connection_pool.disconnect()

    def _send_command_parse_response(self, conn, command_name, *args, **options):
        """
        Send a command and parse the response
        """
        conn.send_command(*args)
        return self.parse_response(conn, command_name, **options)

    # COMMAND EXECUTION AND PROTOCOL PARSING
    def execute_command(self, *args, **options):
        """Execute a command and return a parsed response"""
        command_name = args[0]
        is_red = options.pop('is_red', False)

        if is_red:
            pool = self.master_conn_pool
            conn = self.master_conn or pool.get_connection(command_name, **options)
        else:
            pool = self.connection_pool
            conn = self.connection or pool.get_connection(command_name, **options)

        try:
            return conn.retry.call_with_retry(
                lambda: self._send_command_parse_response(
                    conn, command_name, *args, **options
                ),
                lambda _: None,
            )
        finally:
            if not self.connection:
                pool.release(conn)

    def parse_response(self, connection, command_name, **options):
        """Parses a response from the Redis server"""
        response = connection.read_response()
        return response
