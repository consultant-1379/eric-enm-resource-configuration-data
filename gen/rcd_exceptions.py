"""This module defines custom exceptions."""


class Error(Exception):
    """The base class for exceptions in RCD."""


class MandatoryEnvironmentVariableNotSetError(Error):
    """Exception raised when mandatory environment variables not set"""


class JSONFileNotAvailable(Error):
    """Exception raised when JSON file is not available for the selected product set version"""


class HelmfileTemplateBuildError(Error):
    """Exception raised when helmfile template build fails."""


class HelmTemplateFailedError(Error):
    """Exception raised when helmfile template fails."""


class FileDownloadError(Error):
    """Exception raised when file download fails."""
