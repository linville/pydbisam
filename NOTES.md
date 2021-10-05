DBISAM Table Structure
======================
The format as defined below is most certainly wrong and probably barely works for a very specific version of DBISAM (I think v4). All values are stored using little-endian.


File Format
-----------

One table per file. The high-level file is structure is as follows:

|  Offset  | Size<br>(bytes) | Description |
|  ------: | ---- | ------------------- |
|  `0x9`   | 8    | Last Updated (IEEE-754, days since the Unix epoch)
|  `0x2D`  | 2    | Row size (bytes)    |
|  `0x200` | 768  | First Column Name   |


Column Definition
-----------------

|  Offset  | Size<br>(bytes) | Description   |
|  ------: | ---- | --------------------- |
|  `0x0`   | 2    | Index (Starts at 1)   |
|  `0x2`   | 162? | Name                  |
|  `0xA4`  | 1    | Type                  |
|  `0xA6`  | 2    | Length (String only)  |


Datatypes
---------

In a byte-packed row, all fields (except boolean) have a trailing byte `\x01` that is not included in the size.

| Id | Name      | Size<br>(bytes) | Description   |
| -- | --------- | --- |----------------------- |
| 1  | String    | Variable | Size defined in column definition at `0xA6` |
| 3  | BLOB      | ? | Not supported. BLOBs are stored in a separate `.blb` file. The data in the `.dat` file is likely an address for the `.blb` file.  |
| 4  | Boolean   | 1 | Missing the trailing `\x01` marker |
| 5  | Short Int | 2 |           |
| 6  | Int       | 4 |           |
| 7  | Double    | 8 | IEEE-754  |
| 11 | Timestamp | 8 | IEEE-754, milliseconds since [AD 1, Jan 0](https://en.wikipedia.org/wiki/List_of_non-standard_dates#January_0) |
| 5383 | Currency | 8 | IEEE-754  |
