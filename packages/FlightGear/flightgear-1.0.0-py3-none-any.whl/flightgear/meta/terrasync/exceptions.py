# SPDX-FileCopyrightText: 2018 Florent Rougon
# SPDX-License-Identifier: GPL-2.0-or-later

"""Exceptions raised by flightgear.meta.terrasync."""

from flightgear.meta.exceptions import FGPyException

# Generic exception class, to be subclassed for each specific kind of
# exception.
class TerraSyncPyException(FGPyException):
    ExceptionShortDescription = \
        "Generic exception for flightgear.meta.terrasync"

class UserError(TerraSyncPyException):
     """Exception raised when the program is used in an incorrect way."""
     ExceptionShortDescription = "User error"

class NetworkError(TerraSyncPyException):
     """Exception raised when getting a network error even after retrying."""
     ExceptionShortDescription = "Network error"

class UnsupportedURLScheme(TerraSyncPyException):
     """Exception raised when asked to handle an unsupported URL scheme."""
     ExceptionShortDescription = "Unsupported URL scheme"

class RepoDataError(TerraSyncPyException):
     """
     Exception raised when getting invalid data from the TerraSync repository."""
     ExceptionShortDescription = "Invalid data from the TerraSync repository"

class InvalidDirIndexFile(RepoDataError):
     """Exception raised when getting invalid data from a .dirindex file."""
     ExceptionShortDescription = "Invalid .dirindex file"
