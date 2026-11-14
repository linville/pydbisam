"""
Parsing of the DBISAM table file format.

Provides _TableReader, the mixin used by PyDBISAM to parse a table's file
header, field definitions and rows.

Copyright (c) 2026 Aaron Linville <aaron@linville.org>
"""

import datetime
import struct

from .field import DELPHI_EPOCH, Field

# Delphi's DateDelta: days from 0001-01-01 to 1899-12-30.
_DELPHI_DATE_DELTA = 693594

_MS_PER_DAY = 24 * 60 * 60 * 1000


class _TableReader:
    """
    Parses a DBISAM table's header, field definitions and rows.

    Mixed into PyDBISAM, which provides `_data`, the table's contents as a
    memoryview.
    """

    _FIELD_INFO_OFFSET = 0x200  # Offset of first field info definition
    _FIELD_INFO_SIZE = 768  # Size of a single field info

    def _read_file_header(self):
        self._md5_checksum = bytes(self._data[0x9 : 0x9 + 16])

        self._total_rows = struct.unpack_from("<I", self._data, 0x29)[0]
        self._row_size = struct.unpack_from("<H", self._data, 0x2D)[0]
        self._total_fields = struct.unpack_from("<H", self._data, 0x2F)[0]

        # Last updated is stored as a Delphi TDateTime minus DateDelta. Round to
        # the nearest millisecond (TDateTime's precision) to drop the error
        # from the floating point conversion.
        delphi_days = struct.unpack_from("<d", self._data, 0x3F)[0] + _DELPHI_DATE_DELTA
        ms = round(delphi_days * _MS_PER_DAY)
        self._last_updated = DELPHI_EPOCH + datetime.timedelta(milliseconds=ms)

        # Treat Delphi's zero date as no date, for consistency with DATE and
        # TIMESTAMP fields. This is unusual: DBISAM sets this whenever the table
        # is modified, so it would only be the zero date in a damaged or
        # hand-crafted file.
        if self._last_updated == DELPHI_EPOCH:
            self._last_updated = None

        desc_length = self._data[0x47]
        if desc_length > 0:
            desc_data = bytes(self._data[0x48 : 0x48 + desc_length])
            desc = desc_data.decode("cp1252", errors="replace")
            self._description = desc.rstrip("\x00")
        else:
            self._description = None

        u_major = struct.unpack_from("<H", self._data, 0xC1)[0]
        u_minor = self._data[0xC3]
        self._user_version = f"{u_major}.{u_minor}"

        field_info_subheader_size = self._total_fields * self._FIELD_INFO_SIZE

        self._data_offset = self._FIELD_INFO_OFFSET + field_info_subheader_size

        # Size of just the non-deleted records
        self._calc_row_area_size = self.total_rows * self.row_size

        # Size of all the records, including deleted ones.
        self._row_area_size = len(self._data) - self._data_offset

        # Calculate deleted rows
        self._deleted_rows, remainder = divmod(
            self._row_area_size - self._calc_row_area_size, self._row_size
        )

        # If the difference between the calculated row area and the measured row area
        # is not evenly divisible by the row size, there is likely an issue.
        if remainder:
            raise OSError(
                "Calculated space for deleted rows is not evenly divisible by the row size.\n"
                f"  Row Size      = {self._row_size}\n"
                f"  Meas Row Area = {self._row_area_size}\n"
                f"  Calc Row Area = {self._calc_row_area_size}\n"
                f"  Diff          = {self._row_area_size - self._calc_row_area_size}\n"
            )

        calc_file_size = (
            self._FIELD_INFO_OFFSET
            + field_info_subheader_size
            + self._calc_row_area_size
        )
        meas_file_size = len(self._data)

        # The calculated file size should always be less than or equal
        # to the measured file size (to account for deleted records).
        if calc_file_size > meas_file_size:
            raise OSError(
                "The actual file size is less than expected. "
                "It should be equal to or greater than calculated size.\n"
                f"Calculated = {calc_file_size} = "
                f"{self._FIELD_INFO_OFFSET} + {field_info_subheader_size} + {self._calc_row_area_size}\n"
                f"Actual     = {meas_file_size}\n"
                f"Diff       = {meas_file_size - calc_file_size}"
            )

    def _read_field_subheader(self):
        offset = self._FIELD_INFO_OFFSET

        self._columns = []

        for _ in range(self._total_fields):
            column = self._read_field_definition(
                self._data[offset : offset + self._FIELD_INFO_SIZE]
            )
            self._columns.append(column)

            offset += self._FIELD_INFO_SIZE

    def _read_field_definition(self, data):
        col_index = struct.unpack_from("<H", data, 0x0)[0]

        size_of_name = data[0x2]
        if size_of_name > 162:
            raise RuntimeError(f"Unexpected size of name field: {size_of_name}")
        col_name_buf = bytes(data[0x3 : 0x3 + size_of_name])

        col_type_id = struct.unpack_from("<H", data, 0xA4)[0]

        # Only applicable to strings
        col_size = struct.unpack_from("<H", data, 0xA6)[0]

        col_offset = struct.unpack_from("<H", data, 0xAC)[0] + 1

        expected_index = len(self._columns) + 1
        if col_index != expected_index:
            raise RuntimeError(
                f"Unexpected field index {col_index}. Expected {expected_index}."
            )

        name = col_name_buf.split(b"\x00", 1)[0].decode("utf-8")

        field = Field(col_type_id, name, col_index, col_size, col_offset)

        return field

    def row(self, index, *, extract_deleted=False):
        total_rows_with_deleted = self.total_rows + self._deleted_rows
        if not 0 <= index < total_rows_with_deleted:
            raise IndexError(
                f"Row index {index} out of range. "
                f"Total rows (including deleted): {total_rows_with_deleted}"
            )

        row_offset = self._data_offset + (index * self._row_size)
        row_data = self._data[row_offset : row_offset + self._row_size]

        row_deleted = row_data[0x0]

        # Not sure the exact behavior of these indexes
        # row_idx_a = row_data[0x1]
        # row_idx_b = row_data[0x5]
        # row_checksum = row_data[0x9 : 0x9 + 16]

        if row_deleted and not extract_deleted:
            return None

        # Debugging output for the row header
        # return [
        #     f"{index:03}",
        #     row_data[: self._columns[0].row_offset].hex().upper(),
        #     row_idx_a,
        #     row_idx_b,
        # ]

        return [field.decode_from_row(row_data) for field in self._columns]
