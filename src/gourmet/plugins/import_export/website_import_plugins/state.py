from enum import Enum


class WebsiteTestState(Enum):
    
    SUCCESS = 5
    FAILED = 0

    # TODO: Determine what this value actually means.
    SUCCESS_UNKNOWN = 4
