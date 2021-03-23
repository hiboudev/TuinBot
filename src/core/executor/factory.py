from typing import Dict, Type

from core.executor.base import CommandParamExecutor
from core.param.params import CommandParam, ParamType
from core.executor.executors import UserParamExecutor, EmojiParamExecutor, FixedValueParamExecutor, IntParamExecutor, \
    TextParamExecutor


class ParamExecutorFactory:
    _executors_by_type: Dict[ParamType, Type[CommandParamExecutor]] = {
        ParamType.USER: UserParamExecutor,
        ParamType.EMOJI: EmojiParamExecutor,
        ParamType.FIXED_VALUE: FixedValueParamExecutor,
        ParamType.INT: IntParamExecutor,
        ParamType.TEXT: TextParamExecutor
    }

    @classmethod
    def get_executor(cls, param: CommandParam) -> CommandParamExecutor:
        if param.param_type not in cls._executors_by_type:
            raise Exception("No param executor for this type!")

        return cls._executors_by_type[param.param_type](param)

    @classmethod
    def get_executor_class(cls, param: CommandParam) -> Type[CommandParamExecutor]:
        if param.param_type not in cls._executors_by_type:
            raise Exception("No param executor for this type!")

        return cls._executors_by_type[param.param_type]
