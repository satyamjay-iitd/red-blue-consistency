from typing import Protocol


class CommandsProtocol(Protocol):
    connection_pool: "ConnectionPool"

    def execute_command(self, *args, **options) -> str | int | None:
        ...


class Commands(CommandsProtocol):
    def incrby(self, key: str, value: int = 1):
        pass

    def set(self, key: str, value: str):
        self.execute_command("SET", key, value)

    def get(self, key: str) -> str:
        return self.execute_command("GET", key)
