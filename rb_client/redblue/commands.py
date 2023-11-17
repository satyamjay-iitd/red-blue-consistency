from typing import Protocol


class CommandsProtocol(Protocol):
    connection_pool: "ConnectionPool"

    IS_ADD_BLUE = True
    num_reds, num_blues = 0, 0

    def execute_command(self, *args, **options) -> str | int | None:
        ...


class Commands(CommandsProtocol):
    def hincrby(self, key: int, field: str, value: int = 1):
        self.execute_command("HINCRBY", key, field, value)

    def hget(self, key: int, field: str):
        return self.execute_command("HGET", key, field)

    def hgetall(self, key: int):
        return self.execute_command("HGETALL", key, is_red=True)

    def set(self, key: str, value: str):
        self.execute_command("SET", key, value)

    def get(self, key: str) -> str:
        return self.execute_command("GET", key)

    def deposit(self, amt: int):
        return self.execute_command("DEP", amt)

    def accrue_int(self, rate: int):
        return self.execute_command("AI", rate)

    def withdraw(self, amt: int):
        return self.execute_command("WIT", amt, is_red=True)

    def balance(self) -> float:
        return float(self.execute_command("BAL"))

    def setadd(self, elem: str):
        if self.IS_ADD_BLUE:
            self.execute_command("SETADDB", elem)
            self.num_blues += 1
        else:
            self.execute_command("SETADDR", elem, is_red=True)
            self.num_reds += 1

        if self.num_reds > self.num_blues:
            print(f"Changing colors {self.num_reds} {self.num_blues}")
            self.IS_ADD_BLUE = (not self.IS_ADD_BLUE)
            self.num_reds = 0
            self.num_blues = 0

    def setrem(self, elem: str):
        if self.IS_ADD_BLUE:
            self.execute_command("SETREMR", elem, is_red=True)
            self.num_reds += 1
        else:
            self.execute_command("SETADDB", elem)
            self.num_blues += 1

        if self.num_reds > self.num_blues:
            print(f"Changing colors {self.num_reds} {self.num_blues}")
            self.IS_ADD_BLUE = (not self.IS_ADD_BLUE)
            self.num_reds = 0
            self.num_blues = 0

    def setread(self):
        return self.execute_command("SETREAD", is_red=True)

    def flush(self):
        return self.execute_command("FLUSHALL")
