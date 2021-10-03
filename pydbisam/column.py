from ctypes import create_string_buffer
import struct

from .field import Field


def parse_columns(self):
    offset = self.column_info_offset

    self.columns = []

    while offset < len(self.data):
        column = self.parse_column_info(offset)
        if not column:
            return

        self.columns.append(column)

        offset += self.column_info_size


def parse_column_info(self, offset):
    fields = struct.unpack_from("<HB 161s HH", self.data, offset)

    col_index = fields[0]
    # col_unknown = fields[1]
    col_name_buf = fields[2]
    col_type_id = fields[3]
    col_size = fields[4]  # Only non-zero for strings

    if col_index != len(self.columns) + 1:
        return None

    field = Field(col_type_id, col_size)
    size = field.size

    name = create_string_buffer(col_name_buf).value.decode("utf-8")

    return {
        "index": col_index,
        "name": name,
        "type": field,
        "size": size,
    }
