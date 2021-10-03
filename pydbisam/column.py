from ctypes import create_string_buffer
from enum import Enum, unique
import struct
import binascii


@unique
class Column(Enum):
    STRING = 1
    BOOLEAN = 4
    SHORT_INTEGER = 5
    INTEGER = 6
    FLOAT = 7

    TIMESTAMP = 11

    CURRENCY = 5383

    def field_size(self):
        if self.name in ["SHORT_INTEGER"]:
            return 2

        if self.name in ["INTEGER"]:
            return 4

        if self.name in ["FLOAT"]:
            return 8

        if self.name in ["CURRENCY"]:
            return 8

        # Length of string is in column definition
        if self.name in ["STRING"]:
            return 0

        raise ValueError(f"{self.name} size is unknown.")


def parse_columns(self):
    offset = 0x200

    self.columns = []

    while offset < len(self.data):
        column = self.parse_column_info(offset)
        if not column:
            return

        self.columns.append(column)

        offset += 768


def parse_column_info(self, offset):
    fields = struct.unpack_from("<HB 161s HH", self.data, offset)

    col_index = fields[0]
    # col_unknown = fields[1]
    col_name_buf = fields[2]
    col_type_id = fields[3]
    col_string_size = fields[4]

    print(f"Parsing column {col_index} info")
    if col_index != len(self.columns) + 1:
        return None

    column = Column(col_type_id)
    size = column.field_size()
    if size == 0:
        size = col_string_size

    name = create_string_buffer(col_name_buf).value.decode("utf-8")

    return {
        "index": col_index,
        "name": name,
        "type": column,
        "size": size,
    }
