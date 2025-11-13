from typing import Any, Callable, Generic, List, Dict, Text, Optional, Tuple, Union, TypeVar, Type
from ewoxcore.decorators.serializable import Serializable

T = TypeVar("T")

@Serializable
class ListModel():
    def __init__(self, items:list[T]=[]) -> None:
        self.items: list[T] = items
