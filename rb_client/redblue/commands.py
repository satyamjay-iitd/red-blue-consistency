from typing import Protocol

CHANGE_AFTER = 100


class CommandsProtocol(Protocol):
    connection_pool: "ConnectionPool"

    IS_ADD_BLUE = True
    num_blues, total_red, total = 0, 0, 0

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
        return float(self.execute_command("BAL", is_red=True))

    def setadd(self, elem):
        self.execute_command("SETADDB", elem)

    def setrem(self, elem):
        self.execute_command("SETADDR", elem, is_red=True)

    def setadddyn(self, elem: str):
        self.total += 1
        if self.IS_ADD_BLUE:
            self.execute_command("SETADDB", elem)
            self.num_blues += 1 if self.num_blues < CHANGE_AFTER else 0
        else:
            self.total_red += 1
            self.execute_command("SETADDR", elem, is_red=True)
            self.num_blues -= 1 if self.num_blues > -CHANGE_AFTER else 0

        if self.num_blues < 0:
            print(f"Changing colors Of Add from Red to Blue")
            self.IS_ADD_BLUE = (not self.IS_ADD_BLUE)
            self.num_reds = 0
            self.num_blues = 0

    def setremdyn(self, elem: str):
        self.total += 1

        if self.IS_ADD_BLUE:
            self.total_red += 1
            self.execute_command("SETREMR", elem, is_red=True)
            self.num_blues -= 1 if self.num_blues > -CHANGE_AFTER else 0
        else:
            self.execute_command("SETADDB", elem)
            self.num_blues += 1 if self.num_blues < CHANGE_AFTER else 0

        if self.num_blues < 0:
            print(f"Changing colors Of Add from Blue to Red")
            self.IS_ADD_BLUE = (not self.IS_ADD_BLUE)
            self.num_reds = 0
            self.num_blues = 0

    def setread(self):
        return self.execute_command("SETREAD", is_red=True)

    def flush(self):
        return self.execute_command("FLUSHALL")
