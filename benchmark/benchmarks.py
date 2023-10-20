import abc
import time
from collections import defaultdict
from rich.progress import track
from rich import print

from clients.bank_client import BankClient
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
      print(f"[red][bold]INCORRECT[/bold] {self.name}[/red]")
    else:
      print(f"{self.name} [green][bold]Correct[/bold] [/green]")
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
      self._client.increment(word)

  @property
  def __len__(self) -> int:
    return len(self._word_list)

  def verify(self) -> bool:
    ground_truth = self._wc_offline()
    to_test = self._client.read_all()
    for k, v in track(to_test.items(), description="[blue]Verifying...[/blue]"):
      if isinstance(k, bytes):    # Redis will return dict[bytes, bytes]
        k = k.decode()
      if ground_truth[k] != int(v):
        return False
    return True

  def _wc_offline(self) -> dict[str, int]:
    wc = defaultdict(int)
    for word in self._word_list:
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
    return self._client.read_balance() == self._bank_offline()

  def __len__(self):
    pass

  @property
  def name(self):
    return "Bank"

  def _bank_offline(self) -> float:
    balance = 0
    for command in track(self._command_list, description="[blue]correctness...[/blue]"):
      if command.startswith('d'):
        balance += int(command.split()[1])
      elif command.startswith('w'):
        balance -= int(command.split()[1])
      elif command.startswith('i'):
        balance += balance * 0.5
    return balance
