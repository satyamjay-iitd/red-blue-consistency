import abc
import math
import time
from collections import defaultdict
from multiprocessing import Pool
from typing import Type, Any

from rich.progress import track
from rich import print

import config
from clients.bank_client import BankClient
from clients.set_client import SetClient
from clients.wc_client import WordCountClient
from utils.util import divide_chunks


class Benchmark(abc.ABC):
    def __init__(self):
        self._pre_msg = f"[green]Now Running[/green]: [bold uu green]{self.name}[/bold uu green]"

    def run(self) -> float:
        print(f"[bold uu yellow]Size: {len(self)}[/bold uu yellow]")
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


def wc(client_cls: Type[WordCountClient], args, word_list):
    client = client_cls(**args)
    # for word in track(word_list, description="Processing..."):
    for word in track(word_list, description="Processing..."):
        word.replace('"', '')
        word.replace("'", '')
        client.increment(word)


class WCBenchmark(Benchmark):
    def __init__(
            self,
            client_cls: Type[WordCountClient],
            args: list[dict[str, Any]],
            txt_file: str = '../data/large.txt'
    ):
        super().__init__()
        self._client = client_cls(**args[0])
        self._client.flush()
        self._num_threads = len(args)

        self._word_list: list[str] = open(txt_file, 'r').read().split()

        self.split_word_list = zip(
            [client_cls]*self._num_threads,
            args,
            list(divide_chunks(self._word_list, self._num_threads))
        )

    def __call__(self, *args, **kwargs):
        with Pool(self._num_threads) as p:
            p.starmap(wc, self.split_word_list)
            p.close()
            p.join()
        self._client.read_all()

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


def bank(client_cls: Type[BankClient], args, cmd_list):
    client = client_cls(**args)
    for command in track(cmd_list, description="Processing..."):
        if command.startswith('d'):
            client.deposit(int(command.split()[1]))
        elif command.startswith('w'):
            client.withdraw(int(command.split()[1]))
        elif command.startswith('i'):
            client.accrue_interest()


class BankBenchmark(Benchmark):
    def __init__(
            self,
            client_cls: Type[BankClient],
            args: list[dict[str, Any]],
            data_file: str = '../data/bank.csv'
    ):
        super().__init__()

        self._client = client_cls(**args[0])
        self._client.flush()
        self._num_threads = len(args)

        self._command_list: list[str] = open(data_file, 'r').read().split('\n')

        self.split_cmd_list = zip(
            [client_cls]*self._num_threads,
            args,
            list(divide_chunks(self._command_list, self._num_threads))
        )

    def __call__(self, *args, **kwargs):
        with Pool(self._num_threads) as p:
            p.starmap(bank, self.split_cmd_list)
            p.close()
            p.join()

    def verify(self) -> bool:
        return math.isclose(float(self._client.read_balance()), self._bank_offline())

    def __len__(self):
        return len(self._command_list)

    @property
    def name(self):
        return "Bank"

    def _bank_offline(self) -> float:
        balance = 0
        for command in track(self._command_list, description="[blue]Verifying Consistency...[/blue]"):
            if command.startswith('d'):
                balance += float(command.split()[1])
            elif command.startswith('w'):
                amt = float(command.split()[1])
                balance -= amt if amt <= balance else 0
            elif command.startswith('i'):
                balance += balance * config.BANK_INTEREST
        return balance


def set_serial(client_cls: Type[SetClient], args, cmd_list):
    client = client_cls(**args)
    for command in track(cmd_list, description="Processing..."):
        command, arg = command.split(" ")
        if command == 'A':
            client.add(arg)
        elif command == 'R':
            client.remove(arg)
        else:
            raise Exception("Bad file")


class SetBenchmark(Benchmark):
    def __init__(
            self,
            client_cls: Type[SetClient],
            args: list[dict[str, Any]],
            data_file: str = '../data/bank.csv'
    ):
        super().__init__()
        self._command_list: list[str] = open(data_file, 'r').read().split('\n')[:-1]

        self._client = client_cls(**args[0])
        self._num_threads = len(args)
    
        self._command_list: list[str] = open(data_file, 'r').read().split('\n')[:-1]
    
        self.split_cmd_list = zip(
            [client_cls]*self._num_threads,
            args,
            list(divide_chunks(self._command_list, self._num_threads))
        )

    def verify(self) -> bool:
        ground_truth = self._set_offline()
        return self._client.verify(ground_truth)

    def __len__(self):
        return len(self._command_list)

    def __call__(self, *args, **kwargs):
        with Pool(self._num_threads) as p:
            p.starmap(set_serial, self.split_cmd_list)
            p.close()
            p.join()

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
