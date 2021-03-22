from command.params.params import CommandParam, ParamType


class ApplicationParams:
    """Parameters used accross many commands."""

    USER = CommandParam("tuin", "Une partie du nom du tuin.", ParamType.USER)
    STOP = CommandParam("stop", "", ParamType.FIXED_VALUE)
    INFO = CommandParam("info", "", ParamType.FIXED_VALUE)
