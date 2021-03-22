from operator import attrgetter
from typing import Tuple, List


class Utils:

    @staticmethod
    def multisort(list_to_sort: List, specs: Tuple):
        for key, reverse in reversed(specs):
            list_to_sort.sort(key=attrgetter(key), reverse=reverse)
        return list_to_sort
