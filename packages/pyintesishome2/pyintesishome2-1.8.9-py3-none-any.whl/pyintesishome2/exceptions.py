""" Exceptions for pyintesishome2 """


class IHConnectionError(Exception):
    """Connection Error"""


class IHAuthenticationError(ConnectionError):
    """Authentication Error"""
