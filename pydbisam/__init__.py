import struct


class PyDBISAM:
    from .column import parse_columns, parse_column_info

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

    def dump(self):
        print("Table Structure")
        print(f"  Total Length: {len(self.data)}")
        print(f"       Columns: {len(self.columns)}")
        print(f"      Row Size: {self.row_size} (Computed: {self.compute_row_size()})")
        print(f"    Rows Count: {self.row_count}")
        print()
        print(f"    Column Info Offset: {self.column_info_offset}")
        print(f"           Data Offset: {self.data_offset}")
        print(f"             Data Size: {self.data_size}")

        for col in self.columns:
            print(
                f"{col['index']}, "
                f"{col['name']}, "
                f"{col['type']}, "
                f"{col['size']} "
            )

    def __read_structure(self):
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
        size = 0
        for col in self.columns:
            size += col["size"]

        return size
