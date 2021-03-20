from command.params.params import CommandParam, ParamType, SingleValueParamConfig


class ApplicationParams:
    """Parameters used accross many commands."""

    USER = CommandParam("tuin", "Le nom ou une partie du nom du tuin.", ParamType.USER)
    STOP = CommandParam("stop", "", ParamType.SINGLE_VALUE, SingleValueParamConfig("stop"))
