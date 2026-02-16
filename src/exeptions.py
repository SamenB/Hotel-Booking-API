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

