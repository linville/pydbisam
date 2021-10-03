from enum import Enum, unique


@unique
class FieldType(int, Enum):
    """
    FieldType maps known DBISAM types to a Python enumeration.

    `_value_` is the type id

    `size` is the type size (for static types, string sizes are
    defined the DBISAM column info)

    """

    STRING = (1, 0)
    BOOLEAN = (4, -1)
    SHORT_INTEGER = (5, 2)
    INTEGER = (6, 4)
    FLOAT = (7, 8)

    TIMESTAMP = (11, -1)

    CURRENCY = (5383, -1)

    def __new__(cls, index, size):
        obj = int.__new__(cls, index)
        obj._value_ = index
        obj._size = size
        return obj

    def get_size(self, col_size):
        if self._size == -1:
            raise TypeError(f"{self.__str__()} not supported.")
        elif self._size and col_size:
            raise TypeError("Both innate size and col_size were provided.")
        elif self._size and not col_size:
            return self._size
        elif self._size == 0 and col_size:
            return col_size
        else:
            raise TypeError("Neither innate size nor col_size were provided.")


class Field:
    def __init__(self, typeid, col_size):
        self.type = FieldType(typeid)
        self.size = self.type.get_size(col_size)


if __name__ == "__main__":
    print("Test out FieldType enum")
    print(FieldType(1))
    print(FieldType(6)._size)

    print("Test out Field class")
    x = Field(1, 30)
    print(x)
