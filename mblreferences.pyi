# python
from typing import Dict, Any
from .mblbooks import Books


class References:
    _biblebooks: Books

    def __init__(self) -> None: ...
    def parse_reference(self, reference: str) -> Dict[str, Any]: ...
