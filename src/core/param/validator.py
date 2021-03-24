from typing import List

from core.executor.factory import ParamExecutorFactory
from core.param.syntax import CommandSyntax
from core.utils.generic_utils import GenericUtils


class SyntaxValidator:

    @classmethod
    def validate_syntaxes(cls, syntaxes: List[CommandSyntax]):
        always_valid_param_count = set()
        for syntax in syntaxes:
            if syntax.always_validate_input_format:
                if syntax.param_count in always_valid_param_count:
                    raise Exception("One of the command syntaxes will never execute!")
                always_valid_param_count.add(syntax.param_count)

            for param in syntax.params:
                # Check than used parameters have a corresponding executor.
                # Already checked indirectly above.
                if not ParamExecutorFactory.has_executor(param.param_type):
                    raise Exception(f"No executor for param type {param.param_type}")

                # Check that used param configs support types of corresponding executors.
                # All type cases are probably not treated.
                exec_class = ParamExecutorFactory.get_executor_class(param.param_type)
                # exec_type = exec_class.TypeChecking
                exec_type = GenericUtils.get_generic_param_type(exec_class, 0, 0)

                for config in param.configs:
                    # print(GenericUtils.get_generic_param_type(exec_class, 0, 0))
                    conf_type = GenericUtils.get_generic_param_type(config.__class__, 0, 0)
                    # print(type(exec_type))
                    # print(isinstance(exec_type, tuple))
                    if exec_type != conf_type:
                        # both are unique type or Union but are different

                        if not isinstance(exec_type, tuple) and isinstance(conf_type, tuple):

                            if exec_type not in conf_type:
                                raise Exception(
                                    (
                                        f"Param config {config.__class__.__name__} doesn't support type {exec_type}"
                                        f" of executor {exec_class.__name__} in syntax '{syntax.title}'!"
                                    ))

                        elif isinstance(exec_type, tuple) and not isinstance(conf_type, tuple):
                            # executor is Union, config is unique type
                            # not managing it, probably there's particular cases
                            raise Exception(
                                (
                                    f"Executor {exec_class.__name__} supports more value types than param config "
                                    f"{config.__class__.__name__} in syntax '{syntax.title}', is it valid?"
                                ))

                        elif isinstance(exec_type, tuple) and isinstance(conf_type, tuple):
                            # both are Union

                            for exec_sub_type in exec_type:
                                if exec_sub_type not in conf_type:
                                    raise Exception(
                                        (
                                            f"Param config {config.__class__.__name__} doesn't support type "
                                            f"{exec_sub_type} of executor {exec_class.__name__} in syntax "
                                            f"'{syntax.title}'!"
                                        ))
