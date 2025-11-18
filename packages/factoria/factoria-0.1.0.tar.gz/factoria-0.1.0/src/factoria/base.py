from abc import ABC, abstractmethod
from typing import List, Union
from pydantic import BaseModel

from factoria.exceptions import IncompleteFactoryError

class BaseFactory(ABC):
    def __init__(self):
        object = self.definition()

        if object is None:
            raise IncompleteFactoryError(f"{self.__class__.__name__} must return a definition.")

        self.objects = [object]

    def make(self) -> Union[BaseModel, List[BaseModel]]:
        return self.objects if len(self.objects) > 1 else self.objects[0]

    def count(self, n: int):
        objects = [self.definition() for _ in range(n)]
        self.objects = objects
        return self

    @abstractmethod
    def definition(self) -> BaseModel:
        raise NotImplementedError
