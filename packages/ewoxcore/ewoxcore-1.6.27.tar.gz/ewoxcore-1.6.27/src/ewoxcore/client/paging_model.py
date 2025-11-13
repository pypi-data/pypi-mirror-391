from typing import Any, Callable, Generic, List, Dict, Text, Optional, Tuple, Union, TypeVar, Type
from ewoxcore.decorators.serializable import Serializable

T = TypeVar("T")

Factory = Union[Callable[[Any], T], type[T]]

@Serializable
class PagingModel(Generic[T]):
    rows: list[T]

    def __init__(self, data:Optional[dict[str, any]]=None, item_factory:Factory[T]=None) -> None:
        self.rows = []

        if data is None:
            self.numRows: int = 0
            self.skip: int = 0
            self.num: int = 0
        else:
            self.numRows: int = data.get("numRows", 0)
            self.skip: int = data.get("skip", 0)
            self.num: int = data.get("num", 0)
            if (item_factory):
                self.rows = [item_factory(u) for u in data.get("rows", []) if u is not None]