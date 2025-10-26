import struct
import sys
import hashlib
import os


class Blob:
    """
    Blob is a class that decodes the blob data from a file.

    `_data` is the memoryview of the blob data

    `_block_size` is the size of the block

    """

    _BLOCK_HEADER_SIZE = 18
    _BLOB_DIR = "blobs"

    def __init__(self, content, block_size):
        self._data = memoryview(content)
        self._block_size = block_size

    def get_blob(self, block_index):
        # print("GET BLOB", block_index, file=sys.stderr)
        content = bytearray()
        if block_index == 0:
            return content

        offset = block_index * self._block_size
        remaining_length = 0
        try:
            while True:
                (prev_block, next_block, length_of_block, blob_index, total_length) = struct.unpack_from("<IIHII", self._data, offset)
                if total_length > 0:
                    remaining_length = total_length
                content_offset = offset + self._BLOCK_HEADER_SIZE
                block_content = bytearray(self._data[content_offset:content_offset+length_of_block])
                content.extend(block_content)
                # print("  BLOCK", int(offset/self._block_size), (prev_block, next_block, length_of_block, blob_index, total_length), length_of_block, total_length, offset, len(self._data), file=sys.stderr)
                # print("    CONTENT HEX", block_content.hex(), file=sys.stderr)
                # print("    CONTENT", block_content, file=sys.stderr)
                
                remaining_length -= length_of_block
                #if next_block == 0:
                if remaining_length <= 0:
                    break
                offset = next_block * self._block_size

        except Exception as e:
            print("ERROR decoding block", e, "offset", offset, file=sys.stderr)
            return bytearray()

        # print("    HASH", self._hash(content), file=sys.stderr)
        # print("    COMPLETE", remaining_length, content, file=sys.stderr)
        return content

    def write_blob_to_content_hash(self, content):
        content_hash = self._hash(content)
        self._write_blob_to_file(content, os.path.join(self._BLOB_DIR, content_hash))
        return content_hash

    def _hash(self, content):
        md5 = hashlib.md5()
        md5.update(content)
        return md5.hexdigest();


    def _write_blob_to_file(self, content, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as file:
            file.write(content)

