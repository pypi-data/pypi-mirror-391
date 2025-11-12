class DPGContainersException(Exception):
    pass

class UnrenderedException(DPGContainersException):
    pass

class NamedChildNotFound(DPGContainersException):
    pass

class UnbindableException(DPGContainersException):
    pass

class UnbindableToItemException(DPGContainersException):
    pass

class TaggedNotFound(DPGContainersException):
    pass
