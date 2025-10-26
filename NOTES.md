DBISAM Table Structure
======================
The format as defined below is most certainly wrong and probably barely works for a very specific version of DBISAM (I think v4). All values are stored using little-endian.


File Format
-----------

One table per file. The first 512 bytes are the file header.

|  Offset  | Size<br>(bytes) | Description |
|  ------: | ---- | -------------------- |
|  `0x9`   | 16   | File signature       |
|  `0x1C`  | 4    | Next ending record   |
|  `0x20`  | 4    | Last record Id       |
|  `0x24`  | 4    | Last autoincrement value |
|  `0x29`  | 4    | Total rows           |
|  `0x2D`  | 2    | Row size (bytes)     |
|  `0x2F`  | 2    | Total fields         |
|  `0x3F`  | 8    | Last updated, IEEE-754, days since 3798/12/28 |
|  `0x47`  | 1    | Description Length   |
|  `0x48`  |      | Description          |
|  `0xC1`  | 2    | User version (major) |
|  `0xC3`  | 1    | User version (minor) |
|  `0x200` | 768  | Start of field definitions |

Field Definition
----------------

|  Offset  | Size<br>(bytes) | Description   |
|  ------: | ---- | --------------------- |
|  `0x0`   | 2    | Index (Starts at 1)   |
|  `0x2`   | 162? | Name                  |
|  `0xA4`  | 1    | Type                  |
|  `0xA6`  | 2    | Length (String only)  |
|  `0xAC`  | 2    | Offset within row     |


Datatypes
---------

| Id | Name      | Size<br>(bytes) | Description   |
| -- | --------- | --- |----------------------- |
| 1  | String    | Variable | Size defined in column definition at `0xA6` |
| 2  | Date      | 4 | Days -1 since [AD 1, Jan 0](https://en.wikipedia.org/wiki/List_of_non-standard_dates#January_0) |
| 3  | BLOB      | 8 | Block index in the `.blb` file. The actual content is stored in blocks with 18-byte headers. |
| 4  | Boolean   | 1 | Missing the trailing `\x01` marker |
| 5  | Short Int | 2 |           |
| 6  | Int       | 4 |           |
| 7  | Double    | 8 | IEEE-754  |
| 11 | Timestamp | 8 | IEEE-754, milliseconds since [AD 1, Jan 0](https://en.wikipedia.org/wiki/List_of_non-standard_dates#January_0) |
| 5383 | Currency | 8 | IEEE-754  |
| 7430 | Autoincrement | 4 | Int  |
| 7431 | MEMO     | 8 | Similar to BLOB, stores text content in the `.blb` file |


Row Definition
--------------

A row in the actual data section of the database has a 26-byte row header. The main field is the first one which denotes that the row has been deleted (deleted rows may be overwritten later but the data remains in-place).

|  Offset  | Size<br>(bytes) | Description |
|  ------: | ---- | ---------------------- |
|  `0x0`   | 2    | Row is deleted (=1)    |
|  `0x2`   | 2    | Index A (Starts at 1)  |
|  `0x5`   | 2    | Index B (Starts at 1)  |
|  `0x9`   | 16   | Checksum (MD5?)        |
|  `0x19`  | 2    | Trailing `\x01` marker |
|  `0x20`  |      | Start of first field   |

Blob Format
-----------

Blobs are stored in a separate `.blb` file and use a block-based structure. Each block has a header followed by content.

Block Header (18 bytes):
|  Offset  | Size<br>(bytes) | Description         |
|  ------: | ---- | ------------------------------ |
|  `0x0`   | 4    | Previous block index           |
|  `0x4`   | 4    | Next block index               |
|  `0x8`   | 2    | Length of block content        |
|  `0xA`   | 4    | Unknown index                  |
|  `0xE`   | 4    | Total length (on first block)  |

The blocks form a linked list structure where:
- Each block points to the next block using the next block index
- The chain ends when next block index is 0
- The first block (index 0) is empty
- Content is stored after the header in each block
- The total length field in the first block indicates the complete blob size
