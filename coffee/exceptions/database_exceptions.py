import re


class Psycopg2Error(Exception):
    def __init__(self, *args, errors=None, **kwargs):
        super().__init__(*args)
        self.errors = errors
        for key, value in kwargs.items():
            setattr(self, key, value)


class UniqueViolationError(Psycopg2Error):
    pass


class NotNullViolationError(Psycopg2Error):
    pass


class ForeignKeyViolationError(Psycopg2Error):
    pass
