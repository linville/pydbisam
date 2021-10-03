import struct


class PyDBISAM:
    from .column import parse_columns, parse_column_info

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

        self.__parse_dbisam()


    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def dump(self):
        print(f"  Total Length: {len(self.data)}")
        print(f"  Row Size: {self.row_size}")
        print(f"  Columns: {len(self.columns)}")

        for col in self.columns:
            print(
                f"{col['index']}, "
                f"{col['name']}, "
                f"{col['type']} "
                f"{col['size']} "
            )

    def __parse_dbisam(self):
        print("Parsing")

        self.row_size = struct.unpack_from("<H", self.data, 0x2D)[0]
        self.parse_columns()
