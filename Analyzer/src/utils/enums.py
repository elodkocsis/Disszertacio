from enum import Enum


class ModelStatus(str, Enum):
    READY = "ready"
    UPDATING = "updating"
    SETTING_UP = "setting_up"
