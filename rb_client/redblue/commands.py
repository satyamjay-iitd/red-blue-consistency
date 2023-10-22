from typing import Protocol


class CommandsProtocol(Protocol):
    connection_pool: "ConnectionPool"

    def execute_command(self, *args, **options) -> str | int | None:
        ...


class Commands(CommandsProtocol):
    def hincrby(self, key: int, field: str, value: int = 1):
        self.execute_command("HINCRBY", key, field, value)

    def hget(self, key: int, field: str):
        return self.execute_command("HGET", key, field)

    def hgetall(self, key: int):
        return self.execute_command("HGETALL", key)

    def set(self, key: str, value: str):
        self.execute_command("SET", key, value)

    def get(self, key: str) -> str:
        return self.execute_command("GET", key)

    def deposit(self, amt: int):
        return self.execute_command("DEP", amt)

    def accrue_int(self, rate: int):
        return self.execute_command("AI", rate)

    def withdraw(self, amt: int):
        return self.execute_command("WIT", amt)

    def balance(self) -> float:
        return float(self.execute_command("BAL"))
