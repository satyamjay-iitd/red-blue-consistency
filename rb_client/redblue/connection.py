import os
import socket
import threading
from itertools import chain
from time import sleep

from redblue.parser import ResponseParser
from redblue.serializer import PythonRespSerializer


def str_if_bytes(value: str | bytes) -> str:
    return (
        value.decode("utf-8", errors="replace") if isinstance(value, bytes) else value
    )


class Encoder:
    "Encode strings to bytes-like and decode bytes-like to strings"

    __slots__ = "encoding", "encoding_errors", "decode_responses"

    def __init__(self, encoding, encoding_errors, decode_responses):
        self.encoding = encoding
        self.encoding_errors = encoding_errors
        self.decode_responses = decode_responses

    def encode(self, value):
        "Return a bytestring or bytes-like representation of the value"
        if isinstance(value, (bytes, memoryview)):
            return value
        elif isinstance(value, bool):
            # special case bool since it is a subclass of int
            raise Exception(
                "Invalid input of type: 'bool'. Convert to a "
                "bytes, string, int or float first."
            )
        elif isinstance(value, (int, float)):
            value = repr(value).encode()
        elif not isinstance(value, str):
            # a value we don't know how to deal with. throw an error
            typename = type(value).__name__
            raise Exception(
                f"Invalid input of type: '{typename}'. "
                f"Convert to a bytes, string, int or float first."
            )
        if isinstance(value, str):
            value = value.encode(self.encoding, self.encoding_errors)
        return value

    def decode(self, value, force=False):
        "Return a unicode string from the bytes-like representation"
        if self.decode_responses or force:
            if isinstance(value, memoryview):
                value = value.tobytes()
            if isinstance(value, bytes):
                value = value.decode(self.encoding, self.encoding_errors)
        return value


class Retry:
    """Retry a specific number of times after a failure"""

    def __init__(
            self,
            backoff,
            retries,
            supported_errors=(ConnectionError, TimeoutError, socket.timeout),
    ):
        """
        Initialize a `Retry` object with a `Backoff` object
        that retries a maximum of `retries` times.
        `retries` can be negative to retry forever.
        You can specify the types of supported errors which trigger
        a retry with the `supported_errors` parameter.
        """
        self._backoff = backoff
        self._retries = retries
        self._supported_errors = supported_errors

    def update_supported_errors(self, specified_errors: list):
        """
        Updates the supported errors with the specified error types
        """
        self._supported_errors = tuple(
            set(self._supported_errors + tuple(specified_errors))
        )

    def call_with_retry(self, do, fail):
        """
        Execute an operation that might fail and returns its result, or
        raise the exception that was thrown depending on the `Backoff` object.
        `do`: the operation to call. Expects no argument.
        `fail`: the failure handler, expects the last error that was thrown
        """
        failures = 0
        while True:
            try:
                return do()
            except self._supported_errors as error:
                failures += 1
                fail(error)
                if self._retries >= 0 and failures > self._retries:
                    raise error
                backoff = self._backoff.compute(failures)
                if backoff > 0:
                    sleep(backoff)


class NoBackoff:

    def __init__(self):
        self._backoff = 0

    def compute(self, failures):
        return self._backoff


class Connection:
    "Manages communication to and from a Redis server"

    def __init__(
            self,
            host="localhost",
            port=7379
    ):
        """
        Initialize a new Connection.
        To specify a retry policy for specific errors, first set
        `retry_on_error` to a list of the error/s to retry on, then set
        `retry` to a valid `Retry` object.
        To retry on TimeoutError, `retry_on_timeout` can also be set to `True`.
        """
        self.pid = os.getpid()
        self.host = host
        self.port = int(port)
        self.retry = Retry(NoBackoff(), 1)

        self._sock = None
        self._parser = ResponseParser(socket_read_size=65536)
        self._encoder = Encoder('utf-8', "strict", True)
        self._command_packer = PythonRespSerializer(self._encoder.encode)
        self._socket_timeout = None

    def __del__(self):
        try:
            self.disconnect()
        except Exception:
            pass

    def connect(self):
        "Connects to the Redis server if not already connected"
        if self._sock:
            return
        try:
            sock = self.retry.call_with_retry(
                lambda: self._connect(), lambda error: self.disconnect(error)
            )
        except socket.timeout:
            raise TimeoutError("Timeout connecting to server")
        except OSError as e:
            raise ConnectionError(e)

        self._sock = sock

        try:
            self._on_connect()
        except Exception as e:
            # clean up after any error in on_connect
            self.disconnect()
            raise e

    def _connect(self):
        "Create a TCP socket connection"
        # we want to mimic what socket.create_connection does to support
        # ipv4/ipv6, but we want to set options prior to calling
        # socket.connect()
        err = None
        for res in socket.getaddrinfo(
                self.host, self.port, 0, socket.SOCK_STREAM
        ):
            family, sock_t, proto, _, socket_address = res
            sock = None
            try:
                sock = socket.socket(family, sock_t, proto)
                # TCP_NODELAY
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

                # connect
                sock.connect(socket_address)

                return sock

            except OSError as _:
                err = _
                if sock is not None:
                    sock.close()

        if err is not None:
            raise err
        raise OSError("socket.getaddrinfo returned an empty list")

    def disconnect(self, *args):
        "Disconnects from the Redis server"
        conn_sock = self._sock
        self._sock = None
        if conn_sock is None:
            return

        if os.getpid() == self.pid:
            try:
                conn_sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass

        try:
            conn_sock.close()
        except OSError:
            pass

    def send_command(self, *args):
        """Pack and send a command to the Redis server"""
        self.send_packed_command(
            self._command_packer.pack(*args),
        )

    def send_packed_command(self, command):
        """Send an already packed command to the Redis server"""
        if not self._sock:
            self.connect()
        try:
            self._sock.sendall(command)
        except socket.timeout:
            self.disconnect()
            raise TimeoutError("Timeout writing to socket")
        except OSError as e:
            self.disconnect()
            if len(e.args) == 1:
                errno, errmsg = "UNKNOWN", e.args[0]
            else:
                errno = e.args[0]
                errmsg = e.args[1]
            raise ConnectionError(f"Error {errno} while writing to socket. {errmsg}.")
        except BaseException:
            # BaseExceptions can be raised when a socket send operation is not
            # finished, e.g. due to a timeout.  Ideally, a caller could then re-try
            # to send un-sent data. However, the send_packed_command() API
            # does not support it so there is no point in keeping the connection open.
            self.disconnect()
            raise

    def read_response(
            self,
            disable_decoding=False,
            *,
            disconnect_on_error=True,
    ):
        """Read the response from a previously sent command"""

        try:
            response = self._parser.read_response(disable_decoding=disable_decoding)
        except socket.timeout:
            if disconnect_on_error:
                self.disconnect()
            raise TimeoutError(f"Timeout")
        except OSError as e:
            if disconnect_on_error:
                self.disconnect()
            raise ConnectionError(
                f"Error while reading" f" : {e.args}"
            )
        except BaseException:
            # Also by default close in case of BaseException.  A lot of code
            # relies on this behaviour when doing Command/Response pairs.
            # See #1128.
            if disconnect_on_error:
                self.disconnect()
            raise

        return response

    def can_read(self, timeout=0):
        """Poll the socket to see if there's data that can be read."""
        sock = self._sock
        if not sock:
            self.connect()

        try:
            return self._parser.can_read(timeout)
        except OSError as e:
            self.disconnect()
            raise ConnectionError(f"Error while reading: {e.args}")

    def _on_connect(self):
        self._parser.on_connect(self)


class ConnectionPool:
    """
    Create a connection pool. ``If max_connections`` is set, then this
    object raises :py:class:`~redis.exceptions.ConnectionError` when the pool's
    limit is reached.

    By default, TCP connections are created unless ``connection_class``
    is specified. Use class:`.UnixDomainSocketConnection` for
    unix sockets.

    Any additional keyword arguments are passed to the constructor of
    ``connection_class``.
    """

    def __init__(
        self,
        **connection_kwargs,
    ):
        self.connection_class = Connection
        self.connection_kwargs = connection_kwargs
        self.max_connections = 2**31

        # a lock to protect the critical section in _checkpid().
        # this lock is acquired when the process id changes, such as
        # after a fork. during this time, multiple threads in the child
        # process could attempt to acquire this lock. the first thread
        # to acquire the lock will reset the data structures and lock
        # object of this pool. subsequent threads acquiring this lock
        # will notice the first thread already did the work and simply
        # release the lock.
        self._fork_lock = threading.Lock()
        self.reset()

    def __repr__(self) -> (str, str):
        return (
            f"{type(self).__name__}"
            f"<{repr(self.connection_class(**self.connection_kwargs))}>"
        )

    def reset(self) -> None:
        self._lock = threading.Lock()
        self._created_connections = 0
        self._available_connections = []
        self._in_use_connections = set()

        # this must be the last operation in this method. while reset() is
        # called when holding _fork_lock, other threads in this process
        # can call _checkpid() which compares self.pid and os.getpid() without
        # holding any lock (for performance reasons). keeping this assignment
        # as the last operation ensures that those other threads will also
        # notice a pid difference and block waiting for the first thread to
        # release _fork_lock. when each of these threads eventually acquire
        # _fork_lock, they will notice that another thread already called
        # reset() and they will immediately release _fork_lock and continue on.
        self.pid = os.getpid()

    def _checkpid(self) -> None:
        # _checkpid() attempts to keep ConnectionPool fork-safe on modern
        # systems. this is called by all ConnectionPool methods that
        # manipulate the pool's state such as get_connection() and release().
        #
        # _checkpid() determines whether the process has forked by comparing
        # the current process id to the process id saved on the ConnectionPool
        # instance. if these values are the same, _checkpid() simply returns.
        #
        # when the process ids differ, _checkpid() assumes that the process
        # has forked and that we're now running in the child process. the child
        # process cannot use the parent's file descriptors (e.g., sockets).
        # therefore, when _checkpid() sees the process id change, it calls
        # reset() in order to reinitialize the child's ConnectionPool. this
        # will cause the child to make all new connection objects.
        #
        # _checkpid() is protected by self._fork_lock to ensure that multiple
        # threads in the child process do not call reset() multiple times.
        #
        # there is an extremely small chance this could fail in the following
        # scenario:
        #   1. process A calls _checkpid() for the first time and acquires
        #      self._fork_lock.
        #   2. while holding self._fork_lock, process A forks (the fork()
        #      could happen in a different thread owned by process A)
        #   3. process B (the forked child process) inherits the
        #      ConnectionPool's state from the parent. that state includes
        #      a locked _fork_lock. process B will not be notified when
        #      process A releases the _fork_lock and will thus never be
        #      able to acquire the _fork_lock.
        #
        # to mitigate this possible deadlock, _checkpid() will only wait 5
        # seconds to acquire _fork_lock. if _fork_lock cannot be acquired in
        # that time it is assumed that the child is deadlocked and a
        # redis.ChildDeadlockedError error is raised.
        if self.pid != os.getpid():
            acquired = self._fork_lock.acquire(timeout=5)
            if not acquired:
                raise Exception("Child Deadlock Error")
            # reset() the instance for the new process if another thread
            # hasn't already done so
            try:
                if self.pid != os.getpid():
                    self.reset()
            finally:
                self._fork_lock.release()

    def get_connection(self, command_name: str, *keys, **options) -> "Connection":
        "Get a connection from the pool"
        self._checkpid()
        with self._lock:
            try:
                connection = self._available_connections.pop()
            except IndexError:
                connection = self.make_connection()
            self._in_use_connections.add(connection)

        try:
            # ensure this connection is connected to Redis
            connection.connect()
            # connections that the pool provides should be ready to send
            # a command. if not, the connection was either returned to the
            # pool before all data has been read or the socket has been
            # closed. either way, reconnect and verify everything is good.
            try:
                if connection.can_read():
                    raise ConnectionError("Connection has data")
            except (ConnectionError, OSError):
                connection.disconnect()
                connection.connect()
                if connection.can_read():
                    raise ConnectionError("Connection not ready")
        except BaseException:
            # release the connection back to the pool so that we don't
            # leak it
            self.release(connection)
            raise

        return connection

    def get_encoder(self) -> Encoder:
        "Return an encoder based on encoding settings"
        kwargs = self.connection_kwargs
        return Encoder(
            encoding=kwargs.get("encoding", "utf-8"),
            encoding_errors=kwargs.get("encoding_errors", "strict"),
            decode_responses=kwargs.get("decode_responses", False),
        )

    def make_connection(self) -> "Connection":
        "Create a new connection"
        if self._created_connections >= self.max_connections:
            raise ConnectionError("Too many connections")
        self._created_connections += 1
        return self.connection_class(**self.connection_kwargs)

    def release(self, connection: "Connection") -> None:
        "Releases the connection back to the pool"
        self._checkpid()
        with self._lock:
            try:
                self._in_use_connections.remove(connection)
            except KeyError:
                # Gracefully fail when a connection is returned to this pool
                # that the pool doesn't actually own
                pass

            if self.owns_connection(connection):
                self._available_connections.append(connection)
            else:
                # pool doesn't own this connection. do not add it back
                # to the pool and decrement the count so that another
                # connection can take its place if needed
                self._created_connections -= 1
                connection.disconnect()
                return

    def owns_connection(self, connection: "Connection") -> int:
        return connection.pid == self.pid

    def disconnect(self, inuse_connections: bool = True) -> None:
        """
        Disconnects connections in the pool

        If ``inuse_connections`` is True, disconnect connections that are
        current in use, potentially by other threads. Otherwise only disconnect
        connections that are idle in the pool.
        """
        self._checkpid()
        with self._lock:
            if inuse_connections:
                connections = chain(
                    self._available_connections, self._in_use_connections
                )
            else:
                connections = self._available_connections

            for connection in connections:
                connection.disconnect()

    def close(self) -> None:
        """Close the pool, disconnecting all connections"""
        self.disconnect()

    def set_retry(self, retry: "Retry") -> None:
        self.connection_kwargs.update({"retry": retry})
        for conn in self._available_connections:
            conn.retry = retry
        for conn in self._in_use_connections:
            conn.retry = retry
