import binascii
from ctypes import create_string_buffer
import struct

from .field import Field


def _read_file_header(self):
    self._md5_checksum = self._data[0x9 : 0x9 + 16]

    self._total_rows = struct.unpack_from("<I", self._data, 0x29)[0]
    self._row_size = struct.unpack_from("<H", self._data, 0x2D)[0]
    self._total_fields = struct.unpack_from("<H", self._data, 0x2F)[0]

    # something = struct.unpack_from("<d", self._data, 0x41)[0]
    self._last_updated = None

    field_info_subheader_size = self._total_fields * self._FIELD_INFO_SIZE

    self._data_offset = self._FIELD_INFO_OFFSET + field_info_subheader_size
    self._data_size = self.total_rows * self.row_size

    # Sanity check that sections add up to file length
    if self._FIELD_INFO_OFFSET + field_info_subheader_size + self._data_size != len(
        self._data
    ):
        raise RuntimeError(
            f"Header + Data != File Size mismatch.\n"
            f"{self._FIELD_INFO_OFFSET} + {field_info_subheader_size} + {self._data_size} "
            f"!= {len(self._data)}"
        )


def _read_field_subheader(self):
    offset = self._FIELD_INFO_OFFSET

    self._columns = []

    for field_index in range(self._total_fields):
        column = self._read_field_definition(
            self._data[offset : offset + self._FIELD_INFO_SIZE]
        )
        self._columns.append(column)

        offset += self._FIELD_INFO_SIZE


def _read_field_definition(self, data):
    col_index = struct.unpack_from("<H", data, 0x0)[0]

    size_of_name = struct.unpack_from("<B", data, 0x2)[0]
    if size_of_name > 162:
        raise RuntimeError(f"Unexpected size of name field: {size_of_name}")
    col_name_buf = struct.unpack_from(f"<{size_of_name}s", data, 0x3)[0]

    col_type_id = struct.unpack_from("<H", data, 0xA4)[0]

    # Only applicable to strings
    col_size = struct.unpack_from("<H", data, 0xA6)[0]

    col_offset = struct.unpack_from("<H", data, 0xAC)[0] + 1

    expected_index = len(self._columns) + 1
    if col_index != expected_index:
        raise RuntimeError(
            f"Unexpected field index {col_index}. Expected {expected_index}."
        )

    name = create_string_buffer(col_name_buf).value.decode("utf-8")

    field = Field(col_type_id, name, col_index, col_size, col_offset)

    return field


def row(self, index):
    if index < 0:
        raise RuntimeError(f"Negative index: {index}")
    elif index >= self.total_rows:
        raise RuntimeError(
            f"Index {index} outside of bounds. Total rows: {self.total_rows}"
        )

    row_offset = self._data_offset + (index * self._row_size)
    row_data = self._data[row_offset : row_offset + self._row_size]

    return [field.decode_from_row(row_data) for field in self._columns]
