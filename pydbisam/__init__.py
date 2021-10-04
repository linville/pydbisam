import datetime
import struct


class PyDBISAM:
    from .column import parse_columns, parse_column_info
    from .row import extract_row, debug_extract_row

    column_info_offset = 0x200  # Offset of first column info
    column_info_size = 768  # Size of column info structure

    def __init__(self, path=None, data: bytes = None):
        if path:
            print(f"Path provided: {path}")

            file = open(path, mode="rb")
            self.data = file.read()
        elif data:
            print("Data provided")

            self.data = data
        else:
            raise ()

        self.__read_structure()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def dump_structure(self):
        print("Table Structure")
        print(f"  Total Length: {len(self.data)}")
        print(f"       Columns: {len(self.columns)}")
        print(f"      Row Size: {self.row_size} (Computed: {self.compute_row_size()})")
        print(f"    Rows Count: {self.row_count}")
        print()
        print(f"    Column Info Offset: {self.column_info_offset}")
        print(f"           Data Offset: {self.data_offset}")
        print(f"             Data Size: {self.data_size}")
        print()
        print(f"         Last Modified: {self.last_updated}")

        for col in self.columns:
            print(
                f"{col.index}, "
                f"{col.name}, "
                f"{col}, "
                f"{col.size}, "
                f"{col.row_offset} "
            )

    def __read_structure(self):
        days = struct.unpack_from("<d", self.data, 0x9)[0]
        self.last_updated = datetime.datetime(1970, 1, 1) + datetime.timedelta(
            days=days
        )

        self.row_size = struct.unpack_from("<H", self.data, 0x2D)[0]

        self.parse_columns()

        self.data_offset = (
            self.column_info_offset + len(self.columns) * self.column_info_size
        )
        self.data_size = len(self.data) - self.data_offset

        if self.data_size % self.row_size:
            print("Row size doesn't evenly divide data size.")
            print(f"  data_size / row_size = {self.data_size / self.row_size}")

        self.row_count = int(self.data_size / self.row_size)

    def compute_row_size(self):
        size = 26  # Leading hash
        for col in self.columns:
            size += col.size + 1

        return size

    def extract_rows(self):
        for row_index in range(self.row_count):
            self.extract_row(row_index)
            # self.debug_extract_row(row_index)
