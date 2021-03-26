from core.param.params import CommandParam, ParamType, TextMinMaxParamConfig


class ApplicationParams:
    """Parameters used accross several commands."""

    USER = CommandParam("tuin", "Une partie du nom du tuin", ParamType.USER, TextMinMaxParamConfig(3))
    STOP = CommandParam("stop", "", ParamType.FIXED_VALUE)
    INFO = CommandParam("info", "", ParamType.FIXED_VALUE)
    LIST = CommandParam("list", "", ParamType.FIXED_VALUE)
    SENTENCE = CommandParam("texte", "Le texte, entre guillemets s'il y a des espaces", ParamType.TEXT)
    RECORDED_MESSAGE = CommandParam(SENTENCE.name,
                                    SENTENCE.description,
                                    ParamType.TEXT,
                                    TextMinMaxParamConfig(max_length=300))
