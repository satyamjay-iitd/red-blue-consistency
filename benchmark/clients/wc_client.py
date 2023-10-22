import abc

import redis
import redblue
from rich.progress import track

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

    @abc.abstractmethod
    def verify(self, ground_truth: dict[str, int]) -> bool:
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
        if config.RDS_REP_IN_SYNC:
            self._client.wait(2, 0)

    def verify(self, ground_truth: dict[str, int]) -> bool:
        for k, v in track(self.read_all().items(), description="[blue]Verifying Consistency...[/blue]"):
            if isinstance(k, bytes):  # Redis will return dict[bytes, bytes]
                k = k.decode()
            if ground_truth[k] != int(v):
                return False
        return True


class RedBlueWCClient(WordCountClient):
    def __init__(self):
        super().__init__()
        self._client = redblue.RedBlue()
        self._key = 1

    def increment(self, key):
        self._client.hincrby(self._key, key, 1)

    def read_count(self, word):
        return self._client.hget(self._key, word)

    def read_all(self):
        return self._client.hgetall(self._key)

    def verify(self, ground_truth: dict[str, int]) -> bool:
        out = eval(self.read_all())
        for k, v in track(out.items(), description="[blue]Verifying Consistency...[/blue]"):
            if isinstance(k, bytes):  # Redis will return dict[bytes, bytes]
                k = k.decode()
            if ground_truth[k] != int(v):
                return False
        return True


if __name__ == '__main__':
    rds = RedBlueWCClient()
    rds.increment('foo')
    rds.increment('bar')
    print(rds.read_count('foo'))
    print(rds.read_all())
