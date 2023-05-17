class BaseFHIRError(Exception):
    pass

class RouteNotImplemented(Exception):
    pass

class FeatureCodeIsEmpty(BaseFHIRError):
    pass


class TypeUnknown(BaseFHIRError):
    pass


class RegexUnrecognizedException(Exception):
    pass
