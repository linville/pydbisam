"""
DBISAM field types and decoding of field values.

Provides FieldType, which maps DBISAM type ids to their sizes, and Field, which
describes a table's field and decodes its value from a row's data.

Copyright (c) 2026 Aaron Linville <aaron@linville.org>
"""

import datetime
import struct
from enum import Enum, unique

# Delphi's TDateTime counts days (with the time as a fraction) from this epoch.
# Applications commonly store TDateTime 0 (i.e. this date) to mean "no date".
DELPHI_EPOCH = datetime.datetime(1899, 12, 30)


@unique
class FieldType(int, Enum):
    """
    FieldType maps known DBISAM types to a Python enumeration.

    `_value_` is the type id

    `size` is the type size (for static types, 0 for string sizes which are
    defined the DBISAM column info)
    """

    STRING = (1, 0)
    DATE = (2, 4)
    BLOB = (3, -1)
    BOOLEAN = (4, 1)
    SHORT_INTEGER = (5, 2)
    INTEGER = (6, 4)
    FLOAT = (7, 8)

    TIMESTAMP = (11, 8)

    CURRENCY = (5383, 8)
    AUTOINCREMENT = (7430, 4)

    def __new__(cls, type_id, size):
        obj = int.__new__(cls, type_id)
        obj._value_ = type_id
        obj._size = size
        return obj

    def get_size(self, col_size):
        if self._size == -1:
            # raise TypeError(f"{self.__str__()} not supported.")
            return 0
        elif self._value_ == FieldType.AUTOINCREMENT:
            return 4
        elif self._size and col_size:
            raise TypeError("Both innate size and col_size were provided.")
        elif self._size and not col_size:
            return self._size
        elif self._size == 0 and col_size:
            # Add 1 for the trailing \x00
            return col_size + 1
        else:
            raise TypeError("Neither innate size nor col_size were provided.")


class Field:
    """
    Field stores the field structure and decodes data from row data

    `_type` is the FieldType

    `_name` is the string name of the field

    `_index` is the index of the field within the row (from 0)

    `_size` is the number of bytes used to store the field

    `_row_offset` is the byte offset from the start of a row
    """

    def __init__(self, typeid, name, index, col_size, col_offset):
        self._type = FieldType(typeid)
        self._name = name
        self._index = index
        self._size = self._type.get_size(col_size)
        self._row_offset = col_offset

    def __str__(self):
        return self._type.__str__()

    @property
    def type(self):
        return self._type

    @property
    def name(self):
        return self._name

    @property
    def size(self):
        return self._size

    @property
    def index(self):
        return self._index

    @property
    def row_offset(self):
        return self._row_offset

    def decode_from_row(self, row_data):
        field_data = row_data[self.row_offset : self.row_offset + self.size]

        # Bool doesn't have a field marking that its empty.
        if self._type is FieldType.BOOLEAN:
            return field_data[0] != 0

        # All other fields include a proceeding byte that will be non-zero
        # if the field has a value and zero if it doesn't.
        if row_data[self.row_offset - 1] == 0:
            return None

        match self._type:
            case FieldType.STRING:
                return (
                    bytes(field_data).decode("cp1252", errors="replace").rstrip("\x00")
                )
            case FieldType.BLOB:
                # Value is likely an address within the separate blob file.
                return None
            case FieldType.DATE:
                days = struct.unpack("<i", field_data)[0]
                if days == 0:
                    return None

                date = datetime.date.fromordinal(days)

                # Treat Delphi's zero date as no date.
                if date == DELPHI_EPOCH.date():
                    return None

                return date
            case FieldType.SHORT_INTEGER:
                return struct.unpack("<h", field_data)[0]
            case FieldType.INTEGER:
                return struct.unpack("<i", field_data)[0]
            case FieldType.FLOAT | FieldType.CURRENCY:
                return struct.unpack("<d", field_data)[0]
            case FieldType.TIMESTAMP:
                milliseconds = struct.unpack("<d", field_data)[0]

                # Out of the box we don't support anything before AD 1.
                # Possibly we could use Astropy, but anybody using datetimes
                # of that scale probably aren't using DBISAM's DateTime field.
                if milliseconds < 24 * 60 * 60 * 1000:
                    return None

                ts = (
                    datetime.datetime.min
                    + datetime.timedelta(milliseconds=milliseconds)
                    - datetime.timedelta(days=1)
                )

                # Treat Delphi's zero date as no date. Only an exact match, since
                # a time-only TDateTime is stored as a time on 1899-12-30.
                if ts == DELPHI_EPOCH:
                    return None

                return ts
            case FieldType.AUTOINCREMENT:
                return struct.unpack("<I", field_data)[0]
            case _:
                raise NotImplementedError(f"Decoding {self._type} is not supported.")
