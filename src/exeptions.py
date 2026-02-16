class BookingsExeption(Exception):
    detail = "Unexpected error"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, **kwargs)


class ObjectNotFoundException(BookingsExeption):
    detail = "Object not found"


class AllRoomsAreBookedException(BookingsExeption):
    detail = "All rooms are booked"


class InvalidDataException(BookingsExeption):
    detail = "Invalid data"


class ObjectAlreadyExistsException(BookingsExeption):
    detail = "Object already exists"

class DatabaseException(BookingsExeption):
    detail = "Database error occurred"

class TokenExpiredException(BookingsExeption):
    detail = "Token expired"

class InvalidTokenException(BookingsExeption):
    detail = "Invalid token"

class InvalidDateRangeException(BookingsExeption):
    detail = "date_to must be after date_from"


def check_date_range(date_from, date_to):
    if date_from >= date_to:
        raise InvalidDateRangeException