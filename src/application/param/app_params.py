from core.param.params import CommandParam, ParamType, TextMinMaxParamConfig


class ApplicationParams:
    """Parameters used accross several commands."""

    USER = CommandParam("tuin", "Une partie du nom du tuin", ParamType.USER, TextMinMaxParamConfig(3))
    STOP = CommandParam("stop", "", ParamType.FIXED_VALUE)
    INFO = CommandParam("info", "", ParamType.FIXED_VALUE)
    LIST = CommandParam("list", "", ParamType.FIXED_VALUE)
    SENTENCE = CommandParam("texte", "Le texte, entre guillemets s'il y a des espaces", ParamType.TEXT)
    # SENTENCE_MAX_300 = CommandParam("texte", "Le texte, entre guillemets s'il y a des espaces", ParamType.TEXT,
    #                                 TextMinMaxParamConfig(max_length=300))
    # SENTENCE_MAX_1000 = CommandParam("texte", "Le texte, entre guillemets s'il y a des espaces", ParamType.TEXT,
    #                                  TextMinMaxParamConfig(max_length=1000))
