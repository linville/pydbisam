import binascii
import datetime
import struct

from .field import Field


class PyDBISAM(object):
    from .extract import (
        row,
        _read_file_header,
        _read_field_subheader,
        _read_field_definition,
    )

    _FIELD_INFO_OFFSET = 0x200  # Offset of first field info definition
    _FIELD_INFO_SIZE = 768  # Size of a single field info

    def __init__(self, path=None, data: bytes = None):
        self._path = None
        self._data_bytes = None
        self._data = None
        self._md5_checksum = None
        self._last_updated = None
        self._total_fields = 0
        self._row_size = 0
        self._total_rows = 0

        if path:
            file = open(path, mode="rb")
            self._path = path
            self._data_bytes = file.read()
        elif data:
            self._path = "In memory"
            self._data_bytes = data
        else:
            return

        self._data = memoryview(self._data_bytes)

        self._read_file_header()
        self._read_field_subheader()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    @property
    def md5_checksum(self):
        return self._md5_checksum

    @property
    def md5_checksum_str(self):
        return binascii.hexlify(self._md5_checksum).decode().upper()

    @property
    def last_updated(self):
        return self._last_updated

    @property
    def total_fields(self):
        return self._total_fields

    @property
    def total_rows(self):
        return self._total_rows

    @property
    def row_size(self):
        return self._row_size

    def dump_structure(self):
        print(f"Table: {self._path}")
        print(f"  MD5 Checksum: 0x{self.md5_checksum_str}")
        print(f"  Last Updated: {self.last_updated}")
        print(f"  Total Fields: {self.total_fields}")
        print(f"      Row Size: {self.row_size}")
        print(f"    Total Rows: {self.total_rows}")
        print()
        print(f"  Column Info Offset: {self._FIELD_INFO_OFFSET}")
        print(f"         Data Offset: {self._data_offset}")
        print(f"           Data Size: {self._data_size}")
        print(f"         File Length: {len(self._data)}")
        print()

        print("Index, Name, Typ, Size, Row Offset")
        for col in self._columns:
            print(
                f"{col.index}, "
                f"{col.name}, "
                f"{col}, "
                f"{col.size}, "
                f"{col.row_offset} "
            )

    def fields(self):
        return [x.name for x in self._columns]

    def rows(self):
        for index in range(self._total_rows):
            yield self.row(index)
