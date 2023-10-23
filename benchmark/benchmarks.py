import abc
import math
import time
from collections import defaultdict
from rich.progress import track
from rich import print

import config
from clients.bank_client import BankClient
from clients.set_client import SetClient
from clients.wc_client import WordCountClient


class Benchmark(abc.ABC):
    def __init__(self):
        self._pre_msg = f"[green]Now Running[/green]: [bold uu green]{self.name}[/bold uu green]"

    def run(self) -> float:
        before = time.time()
        self()
        total_time = time.time() - before
        print(f"[bold uu yellow]Took {total_time}s[/bold uu yellow]")
        print()
        if not self.verify():
            print(f"[red][bold]INCONSISTENT[/bold] {self.name}[/red]")
        else:
            print(f"{self.name} [green][bold]CONSISTENT[/bold] [/green]")
        return total_time

    @abc.abstractmethod
    def verify(self) -> bool:
        pass

    @abc.abstractmethod
    def __len__(self):
        pass

    @abc.abstractmethod
    def __call__(self, *args, **kwargs):
        pass

    @property
    @abc.abstractmethod
    def name(self):
        pass


class WCBenchmark(Benchmark):
    def __init__(self, client: WordCountClient, txt_file: str = '../data/large.txt'):
        super().__init__()
        self._word_list: list[str] = open(txt_file, 'r').read().split()
        self._client: WordCountClient = client

    def __call__(self, *args, **kwargs):
        for word in track(self._word_list, description="Processing..."):
            word.replace('"', '')
            word.replace("'", '')
            self._client.increment(word)
        self._client.read_all()

    @property
    def __len__(self) -> int:
        return len(self._word_list)

    def verify(self) -> bool:
        ground_truth = self._wc_offline()
        return self._client.verify(ground_truth)

    def _wc_offline(self) -> dict[str, int]:
        wc = defaultdict(int)
        for word in self._word_list:
            word.replace('"', '')
            word.replace("'", '')

            wc[word] += 1
        return wc

    @property
    def name(self):
        return "Word Count"


class BankBenchmark(Benchmark):
    def __init__(self, client: BankClient, data_file: str = '../data/bank.csv'):
        super().__init__()
        self._command_list: list[str] = open(data_file, 'r').read().split('\n')
        self._client: BankClient = client

    def __call__(self, *args, **kwargs):
        for command in track(self._command_list, description="Processing..."):
            if command.startswith('d'):
                self._client.deposit(int(command.split()[1]))
            elif command.startswith('w'):
                self._client.withdraw(int(command.split()[1]))
            elif command.startswith('i'):
                self._client.accrue_interest()

    def verify(self) -> bool:
        return math.isclose(float(self._client.read_balance()), self._bank_offline())

    def __len__(self):
        return self._command_list

    @property
    def name(self):
        return "Bank"

    def _bank_offline(self) -> float:
        balance = 0
        for command in track(self._command_list, description="[blue]Verifying Consistency...[/blue]"):
            if command.startswith('d'):
                balance += float(command.split()[1])
            elif command.startswith('w'):
                balance -= float(command.split()[1])
            elif command.startswith('i'):
                balance += balance * config.BANK_INTEREST
        return balance


class SetBenchmark(Benchmark):
    def __init__(self, client: SetClient, data_file: str = '../data/bank.csv'):
        super().__init__()
        self._command_list: list[str] = open(data_file, 'r').read().split('\n')[:-1]
        self._client: SetClient = client

    def verify(self) -> bool:
        ground_truth = self._set_offline()
        return self._client.verify(ground_truth)

    def __len__(self):
        return self._command_list

    def __call__(self, *args, **kwargs):
        for command in track(self._command_list, description="Processing..."):
            command, arg = command.split(" ")
            if command == 'A':
                self._client.add(arg)
            elif command == 'R':
                self._client.remove(arg)
            else:
                raise Exception("Bad file")

    @property
    def name(self):
        return "Set"

    def _set_offline(self) -> set[str]:
        final = set()
        for command in track(self._command_list, description="[blue]Verifying Consistency...[/blue]"):
            command, arg = command.split(" ")
            if command == 'A':
                final.add(arg)
            elif command == 'R':
                final.discard(arg)
            else:
                raise Exception("Bad file")

        return final
