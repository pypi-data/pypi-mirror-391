""" Processing Enum """
from enum import auto
from yk_utils.models import StrBaseEnum


class ProcessingEnum(str, StrBaseEnum):
    """ ProcessingEnum """

    detect = auto()
    analyze = auto()
    templify = auto()
    none = auto()
