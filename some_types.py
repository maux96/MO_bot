from typing import TypedDict, List


class VarDescript(TypedDict):
    name: str
    text: str

class ProblemInfo(TypedDict):
    id: int
    title: str
    text: str
    used_vars:  List[VarDescript]
    used_params: List[VarDescript]