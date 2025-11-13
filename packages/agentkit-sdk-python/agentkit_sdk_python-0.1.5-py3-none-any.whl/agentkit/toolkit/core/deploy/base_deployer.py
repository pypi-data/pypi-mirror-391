from abc import ABC, abstractmethod


class BaseDeployer(ABC):
    @abstractmethod
    def deploy(self): ...
