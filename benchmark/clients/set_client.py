import abc

import redis
import redblue

import config


class SetClient(abc.ABC):
    def __init__(self):
        pass

    @abc.abstractmethod
    def add(self, word: str):
        pass

    @abc.abstractmethod
    def remove(self, word: str):
        pass

    @abc.abstractmethod
    def read(self) -> set[str]:
        pass

    @abc.abstractmethod
    def verify(self, ground_truth: set[str]) -> bool:
        pass


class RedisSetClient(SetClient):
    def __init__(self, flush=True):
        super().__init__()
        self._client = redis.client.Redis(port=config.RDS_MASTER_PORT, decode_responses=True)
        self._client.flushdb() if flush else None
        self._key = '_set_'

    def add(self, word: str):
        self._client.sadd(self._key, word)
        self._sync_replicas()

    def remove(self, word: str):
        self._client.srem(self._key, word)
        self._sync_replicas()

    def read(self) -> set[str]:
        return self._client.smembers(self._key)

    def verify(self, ground_truth: set[str]) -> bool:
        return self.read() == ground_truth

    def _sync_replicas(self):
        if config.RDS_REP_IN_SYNC:
            self._client.wait(2, 0)


class RedBlueSetClient(SetClient):
    def __init__(self, port=7379):
        super().__init__()
        self._client = redblue.RedBlue(port=port)
        self._key = 1
        self._dynamic = True

    def add(self, word: str):
        if self._dynamic:
            self._client.setadddyn(word)
        else:
            self._client.setadd(word)

    def remove(self, word: str):
        if self._dynamic:
            self._client.setremdyn(word)
        else:
            self._client.setrem(word)

    def read(self) -> set[str]:
        return {word for word in self._client.setread().split()}

    def verify(self, ground_truth: set[str]) -> bool:
        return self.read() == ground_truth
