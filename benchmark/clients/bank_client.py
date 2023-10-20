import abc

import redis

import config


class BankClient(abc.ABC):
  def __init__(self):
    pass

  @abc.abstractmethod
  def deposit(self, money: float):
    pass

  @abc.abstractmethod
  def withdraw(self, money: float) -> None:
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
    self._key = 'bank'

  def deposit(self, money: float):
    self._client.incrbyfloat(self._key, money)

  def withdraw(self, money: float) -> None:
    self._client.incrbyfloat(self._key, -money)

  def accrue_interest(self) -> None:
    self._client.fcall('accrue_interest', 1, self._key, config.BANK_INTEREST)

  def read_balance(self) -> float:
    return self._client.get(self._key)


class RedBlueBankClient(BankClient):

  def deposit(self, money: int):
    pass

  def withdraw(self, money: int) -> None:
    pass

  def accrue_interest(self) -> None:
    pass

  def read_balance(self) -> float:
    pass
