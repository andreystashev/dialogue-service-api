from fastapi import status

from .domain_exception import DomainException


# Users (1xx)
class UserExistException(DomainException):
    status_code: int = status.HTTP_409_CONFLICT
    error_details: str = "A user with such credentials already exists"
    error_code: int = 105


class UserNotFoundException(DomainException):
    status_code: int = status.HTTP_404_NOT_FOUND
    error_details: str = "User not found"
    error_code: int = 106


class PasswordNotConfirmedException(DomainException):
    status_code: int = status.HTTP_400_BAD_REQUEST
    error_details: str = "The entered passwords do not match"
    error_code: int = 107


class PasswordIsNotSecureException(DomainException):
    status_code: int = status.HTTP_400_BAD_REQUEST
    error_details: str = "The password must be at least 8 characters long"
    error_code: int = 108


# Auth and JWT (2xx)
class AccessDeniedException(DomainException):
    status_code: int = status.HTTP_403_FORBIDDEN
    error_details: str = "Access denied"
    error_code: int = 201


class InvalidCredentialsException(DomainException):
    status_code: int = status.HTTP_401_UNAUTHORIZED
    error_details: str = "Incorrect username or password"
    error_code: int = 202


class InactiveUserProfileException(DomainException):
    status_code: int = status.HTTP_400_BAD_REQUEST
    error_details: str = "The user profile is not activated"
    error_code: int = 203


class JwtInactiveTokenException(DomainException):
    status_code: int = status.HTTP_403_FORBIDDEN
    error_details: str = "JWT token is blocked"
    error_code: int = 204


class JwtInvalidTokenException(DomainException):
    status_code: int = status.HTTP_400_BAD_REQUEST
    error_details: str = "The JWT token is incorrect"
    error_code: int = 205


class JwtExpiredTokenException(DomainException):
    status_code: int = status.HTTP_400_BAD_REQUEST
    error_details: str = "The JWT token has expired"
    error_code: int = 206


class JwtTokenNotExistsException(DomainException):
    status_code: int = status.HTTP_409_CONFLICT
    error_details: str = "The JWT token does not exist"
    error_code: int = 207


# Dialogs (3xx)
class DialogNotFoundException(DomainException):
    status_code: int = status.HTTP_404_NOT_FOUND
    error_details: str = "Dialog Not Found"
    error_code: int = 301
