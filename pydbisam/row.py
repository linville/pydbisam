import binascii
import struct


def extract_row(self, index):
    row_offset = self.data_offset + index * self.row_size
    row_data = self.data[row_offset : row_offset + self.row_size]

    # print(binascii.hexlify(row_data, " "))
    # print(binascii.b2a_qp(row_data))

    print()
    for col in self.columns:
        print(
            f"{col.index}, ",
            f"{col.name}, ",
            f"{col.type}, ",
            f"{col.row_offset}, ",
            f"{col.size}, ",
            f'"{col.decode_from_row(row_data)}"',
        )
