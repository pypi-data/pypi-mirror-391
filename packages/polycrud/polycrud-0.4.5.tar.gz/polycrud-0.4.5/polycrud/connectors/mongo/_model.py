from enum import Enum

import pymongo


class Sort(Enum):
    DESCENDING = pymongo.DESCENDING
    ASCENDING = pymongo.ASCENDING
