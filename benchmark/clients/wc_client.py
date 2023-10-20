import abc

import redis

import config


class WordCountClient(abc.ABC):
  def __init__(self):
    pass

  @abc.abstractmethod
  def increment(self, word: str):
    pass

  @abc.abstractmethod
  def read_count(self, word: str) -> int:
    pass

  @abc.abstractmethod
  def read_all(self) -> dict[str | bytes, int | bytes]:
    pass


class RedisWCClient(WordCountClient):
  def __init__(self, flush=True):
    super().__init__()
    self._client = redis.client.Redis(port=config.RDS_MASTER_PORT)
    self._client.flushdb() if flush else None
    self._key = 'word_count'

  def read_count(self, word):
    return self._client.hget(self._key, word)

  def read_all(self):
    return self._client.hgetall(self._key)

  def increment(self, key):
    self._client.hincrby(self._key, key, 1)


class RedBlueWCClient(WordCountClient):

  def increment(self, key):
    pass

  def read_count(self, word):
    pass

  def read_all(self):
    pass


if __name__ == '__main__':
  rds = RedisWCClient()
  rds.increment('foo')
  rds.increment('bar')
  print(rds.read_count('foo'))
  print(rds.read_all())
