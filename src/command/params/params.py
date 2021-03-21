import sys
from enum import Enum


class ParamType(Enum):
    USER = 1
    EMOJI = 2
    SINGLE_VALUE = 3
    INT = 4


class ParamResultType(Enum):
    VALID = 1
    INVALID = 2


class ParamConfig:
    pass


# TODO à priori il n'y a pas besoin de config pour ça, on peut utiliser le nom du param pour la valeur
class SingleValueParamConfig(ParamConfig):

    def __init__(self, single_value: str):
        self.single_value = single_value


class IntParamConfig(ParamConfig):

    def __init__(self, min_value: int = 0, max_value: int = sys.maxsize):
        self.min_value = min_value
        self.max_value = max_value


class CommandParam:

    def __init__(self, name: str, description: str, param_type: ParamType, config: ParamConfig = None):
        # if param_type == ParamType.SINGLE_VALUE and single_value is None \
        #         or param_type != ParamType.SINGLE_VALUE and single_value is not None:
        #     raise Exception("param_type and single_value are not coherents!")

        self.name = name
        self.description = description
        self.param_type = param_type
        self.config = config

    @property
    def single_value(self) -> str:
        if not isinstance(self.config, SingleValueParamConfig):
            raise Exception("Param is not a SingleValueParamConfig!")

        return self.config.single_value
