DBISAM Table Structure
======================
The format as defined below is most certainly wrong and probably barely works for a very specific version of DBISAM (I think v4). All values are stored using little-endian.


File Format
-----------

One table per file. The first 512 bytes are the file header.

|  Offset  | Size<br>(bytes) | Description |
|  ------: | ---- | -------------------- |
|  `0x9`   | 16   | File Signature?      |
|  `0x29`  | 4    | Total rows           |
|  `0x2D`  | 2    | Row size (bytes)     |
|  `0x2F`  | 2    | Total fields         |
|  `0x41`  | 5?   | Last Updated?        |
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
| 3  | BLOB      | ? | Not yet supported. BLOBs are stored in a separate `.blb` file. The data in the `.dat` file is likely an address for the `.blb` file.  |
| 4  | Boolean   | 1 | Missing the trailing `\x01` marker |
| 5  | Short Int | 2 |           |
| 6  | Int       | 4 |           |
| 7  | Double    | 8 | IEEE-754  |
| 11 | Timestamp | 8 | IEEE-754, milliseconds since [AD 1, Jan 0](https://en.wikipedia.org/wiki/List_of_non-standard_dates#January_0) |
| 5383 | Currency | 8 | IEEE-754  |


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
