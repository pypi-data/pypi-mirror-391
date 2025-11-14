from abc import ABCMeta, abstractmethod
from os import PathLike
from pathlib import Path
from typing import Generic, Iterable, TypeVar

from fsspec.implementations.local import LocalFileSystem
from fsspec.spec import AbstractFileSystem

from .split_data import AbstractSplitData

_ElementType = TypeVar('_ElementType')


class AbstractDatasetManager(Generic[_ElementType], metaclass=ABCMeta):

    def __init__(self, path: str | PathLike, file_system: AbstractFileSystem | None = None):
        self._fs = file_system if file_system else LocalFileSystem()
        self._path = Path(path)

    @abstractmethod
    def add(self, element: _ElementType) -> None:
        ...

    def update(self, elements: Iterable[_ElementType]) -> None:
        for element in elements:
            self.add(element)

    @abstractmethod
    def remove(self, element: _ElementType) -> None:
        ...

    @abstractmethod
    def save(self, version: str | None = None, exist_ok: bool = False) -> None:
        # TODO: reconsider the `version` parameter in the interface.
        #  It might be better to remove it from the interface and handle it via an implementation-level setter,
        #  since not all managers support the concept of versions.
        ...

    @abstractmethod
    def get_dataset(self) -> AbstractSplitData:
        ...
