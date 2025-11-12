class V2ShareError(Exception):
    """Base class for all vaxbnana exceptions"""


class NotSupportedError(V2ShareError):
    """indicating that the proxy is somehow not supported by vaxbnana"""


class TransportNotSupportedError(NotSupportedError):
    """indicating that the specified transport is not supported"""


class ProtocolNotSupportedError(NotSupportedError):
    """indicating that the protocol is not supported"""
