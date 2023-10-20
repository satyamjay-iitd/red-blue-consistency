import abc

import redis

import config


class BankClient(abc.ABC):
  def __init__(self):
    pass

  @abc.abstractmethod
  def deposit(self, money: int):
    pass

  @abc.abstractmethod
  def withdraw(self, money: int) -> None:
    pass

  @abc.abstractmethod
  def accrue_interest(self) -> None:
    pass

  @abc.abstractmethod
  def read_balance(self) -> float:
    pass


class RedisBankClient(BankClient):
  def __init__(self, flush=True):
    super().__init__()
    self._client = redis.client.Redis(port=config.RDS_MASTER_PORT)
    self._client.flushdb() if flush else None
    self._key = 'bank_account'

  def deposit(self, money: int):
    self._client.incrby(self._key, money)

  def withdraw(self, money: int) -> None:
    self._client.incrby(self._key, -money)

  def accrue_interest(self) -> None:
    self._client.fcall('accrue_interest', 1, [self._key])

  def read_balance(self) -> float:
    return int(self._client.get(self._key))
