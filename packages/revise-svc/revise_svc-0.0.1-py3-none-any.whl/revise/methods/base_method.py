from abc import ABC
from abc import abstractmethod


class BaseMethod(ABC):
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

    @abstractmethod
    def run(self, *args, **kwargs):
        raise NotImplementedError("run method not implemented")
