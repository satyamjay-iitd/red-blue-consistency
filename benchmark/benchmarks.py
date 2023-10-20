import abc
import time
from collections import defaultdict
from rich.progress import track
from rich import print

from clients.wc_client import WordCountClient


class Benchmark(abc.ABC):
  def __init__(self):
    self._pre_msg = f"[green]Now Running[/green]: [bold uu green]{self.name}[/bold uu green]"

  def run(self) -> float:
    before = time.time()
    self()
    total_time = time.time() - before
    print(f"[bold uu yellow]Took {total_time}s[/bold uu yellow]")
    print("[blue]Verifying correctness...[/blue]")
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

    for k, v in to_test.items():
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
