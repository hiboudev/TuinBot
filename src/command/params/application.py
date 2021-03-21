from command.params.params import CommandParam, ParamType


class ApplicationParams:
    """Parameters used accross many commands."""

    USER = CommandParam("tuin", "Le nom du tuin, ou une partie du nom.", ParamType.USER)
    STOP = CommandParam("stop", "", ParamType.FIXED_VALUE)
