import sys
from enum import Enum


class ParamType(Enum):
    USER = 1
    EMOJI = 2
    FIXED_VALUE = 3
    INT = 4


class ParamResultType(Enum):
    VALID = 1
    INVALID = 2


class ParamConfig:
    pass


class IntParamConfig(ParamConfig):

    def __init__(self, min_value: int = 0, max_value: int = sys.maxsize):
        self.min_value = min_value
        self.max_value = max_value


class CommandParam:

    def __init__(self, name: str, description: str, param_type: ParamType, config: ParamConfig = None):
        self.name = name
        self.description = description
        self.param_type = param_type
        self.config = config
