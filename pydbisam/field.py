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

    `type` is the FieldType

    `size` is the number of bytes used to store the field

    `index` is the index of the field within the row (from 0)

    `row_offset` is the byte offset from the start of a row
    """

    def __init__(self, typeid, name, col_size, index):
        self.type = FieldType(typeid)
        self.name = name
        self.size = self.type.get_size(col_size)
        self.index = index
        self.row_offset = 0

    def __str__(self):
        return self.type.__str__()

    def decode_from_row(self, row_data):
        field_data = row_data[self.row_offset : self.row_offset + self.size]

        if self.type is FieldType.STRING:
            return create_string_buffer(field_data).value.decode("utf-8")
        if self.type is FieldType.BLOB:
            # Value is likely an address within the separate blob file.
            return None
        elif self.type is FieldType.BOOLEAN:
            return struct.unpack("<b", field_data)[0]
        elif self.type is FieldType.SHORT_INTEGER:
            return struct.unpack("<h", field_data)[0]
        elif self.type is FieldType.INTEGER:
            return struct.unpack("<i", field_data)[0]
        elif self.type is FieldType.FLOAT:
            return struct.unpack("<d", field_data)[0]
        elif self.type is FieldType.TIMESTAMP:
            milliseconds = struct.unpack("<d", field_data)[0]

            ts = datetime.datetime(1, 1, 1)
            ts += datetime.timedelta(milliseconds=milliseconds)
            ts -= datetime.timedelta(days=1)

            return ts
        elif self.type is FieldType.CURRENCY:
            return struct.unpack("<d", field_data)[0]
        elif self.type is FieldType.AUTOINCREMET:
            return struct.unpack("<i", field_data)[0]
        else:
            return None


if __name__ == "__main__":
    print("Test out FieldType enum")
    print(FieldType(1))
    print(FieldType(6)._size)

    print("Test out Field class")
    x = Field(1, 30)
    print(x)
