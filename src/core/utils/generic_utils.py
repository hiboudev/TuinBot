from typing import Type, get_args, Union, get_origin


class GenericUtils:

    @staticmethod
    def get_generic_param_type(clazz: type, parent_level: int, param_index: int) -> type:
        # noinspection PyUnresolvedReferences
        param_type = get_args(clazz.__orig_bases__[parent_level])[param_index]
        if get_origin(param_type) is Union:
            # noinspection PyTypeChecker
            return get_args(param_type)
        return param_type
