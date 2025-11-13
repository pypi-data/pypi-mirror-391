from typing import Any, Callable, Generic, List, Dict, Text, Optional, Tuple, Union, TypeVar, Type
from ewoxcore.decorators.serializable import Serializable

@Serializable
class PagingArgs():
    def __init__(self, data:Optional[dict[str, any]]=None) -> None:
        if data is None:
            self.search: str = ""
            self.skip: int = 0
            self.num: int = 10
            self.sortField: str = ""
            self.sortDir: str = "asc"
        else:
            self.search: str = data.get("search", "")
            self.skip: int = data.get("skip", 0)
            self.num: int = data.get("num", 10)
            self.sortField: str = data.get("sortField", "")
            self.sortDir: str = data.get("sortDir", "asc")


    def to_dict(self) -> Dict[str, Any]:
        return {
            "search": self.search,
            "skip": self.skip,
            "num": self.num,
            "sortField": self.sortField,
            "sortDir": self.sortDir,
        }
