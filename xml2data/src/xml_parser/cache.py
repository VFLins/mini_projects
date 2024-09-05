import pickle
from os import path, makedirs


SCRIPT_PATH = path.split(path.realpath(__file__))[0]
CACHE_PATH = path.join(SCRIPT_PATH, "cache")
CACHE_TYPES = ["passed", "failed", "keys"]

makedirs(CACHE_PATH, exist_ok=True)


class AlreadyProcessedError(Exception):
    """Indica que um arquivo já foi processado antes."""
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class CacheHandler:
    def __init__(self, cachename: str) -> None:
        self.cachefile = path.join(CACHE_PATH, cachename + ".cache")
        self.data = self.load()

    def load(self) -> list:
        with open(self.cachefile, "r") as cache:
            return pickle.load(cache)

    def add(self, item) -> None:
        cached = self.load()

        if item in cached:
            raise AlreadyProcessedError("Este arquivo já foi processado antes")

        if len(self.data) != len(cached):
            self._heal()

        with open(self.cachefile, "wb") as cache:
            pickle.dump(obj=self.data + [item], file=cache)

        self.data = self.load()

    def _heal(self) -> None:
        # TODO: Warn inconsistent sizes
        cached = self.load()
        count = 0
        for item in cached:
            if item not in self.data:
                self.data.append(item)
                count = count + 1
        # TODO: Info how many items were restored from cache to memory