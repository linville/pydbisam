import binascii
from enum import Enum, unique
import datetime
from ctypes import create_string_buffer
import struct


@unique
class FieldType(int, Enum):
    """
    FieldType maps known DBISAM types to a Python enumeration.

    `_value_` is the type id

    `size` is the type size (for static types, 0 for string sizes which are
    defined the DBISAM column info)
    """

    STRING = (1, 0)
    # DATE = (2, ?)
    BLOB = (3, -1)
    BOOLEAN = (4, 1)
    SHORT_INTEGER = (5, 2)
    INTEGER = (6, 4)
    FLOAT = (7, 8)

    TIMESTAMP = (11, 8)

    CURRENCY = (5383, 8)
    AUTOINCREMET = (7430, 8)

    def __new__(cls, type_id, size):
        obj = int.__new__(cls, type_id)
        obj._value_ = type_id
        obj._size = size
        return obj

    def get_size(self, col_size):
        if self._size == -1:
            # raise TypeError(f"{self.__str__()} not supported.")
            return 0
        elif self._size and col_size:
            raise TypeError("Both innate size and col_size were provided.")
        elif self._size and not col_size:
            return self._size
        elif self._size == 0 and col_size:
            # Add 2 for leading \x01 and trailing \x00
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

    def decode_from_row(self, row_data):  # noqa: C901
        field_data = row_data[self.row_offset : self.row_offset + self.size]

        if self._type is FieldType.STRING:
            return (
                bytearray(field_data).decode("cp1252", errors="replace").rstrip("\x00")
            )
        if self._type is FieldType.BLOB:
            # Value is likely an address within the separate blob file.
            return None
        elif self._type is FieldType.BOOLEAN:
            return struct.unpack("<b", field_data)[0]
        elif self._type is FieldType.SHORT_INTEGER:
            return struct.unpack("<h", field_data)[0]
        elif self._type is FieldType.INTEGER:
            return struct.unpack("<i", field_data)[0]
        elif self._type is FieldType.FLOAT:
            return struct.unpack("<d", field_data)[0]
        elif self._type is FieldType.TIMESTAMP:
            milliseconds = struct.unpack("<d", field_data)[0]

            # Out of the box we don't support anything before AD 1.
            # Possibly we could use Astropy, but anybody using datetimes
            # of that scale probably aren't using DBISAM's DateTime field.
            if milliseconds < 24 * 60 * 60 * 1000:
                return None

            ts = datetime.datetime(1, 1, 1)
            ts += datetime.timedelta(milliseconds=milliseconds)
            ts -= datetime.timedelta(days=1)

            return ts
        elif self._type is FieldType.CURRENCY:
            return struct.unpack("<d", field_data)[0]
        elif self._type is FieldType.AUTOINCREMET:
            return struct.unpack("<i", field_data)[0]
        else:
            return "Fail"


if __name__ == "__main__":
    print("Test out FieldType enum")
    print(FieldType(1))
    print(FieldType(6)._size)

    print("Test out Field class")
    x = Field(1, "Test", 8, 1)
    print(x)
