from typing import Optional


class AppError(Exception):
    """Base de los errores de dominio. La capa HTTP los traduce a respuestas en `app.main`."""

    message = "Unknown error"

    def __init__(self, message: Optional[str] = None):
        super().__init__(message or self.message)


class InvalidIdError(AppError):
    message = "Invalid ID format"


class AppNotFoundError(AppError):
    message = "Application not found"


class AppAlreadyInactiveError(AppError):
    message = "Application is already inactive"
