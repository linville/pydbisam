DBISAM Structure
================
The format as defined below is most certainly wrong and probably barely works for a very specific version of DBISAM (I think v4).


DBISAM File Format
------------------

One table per file. The high-level file is 

|  Offset  | Size | Description |
|  ------- | ---- | -------------       |
|  `0x2d`  | 2    | Row size (bytes)    |
|  `0x200` | 768  | First Column Name   |


DBISAM Column Definition
------------------------

|  Offset  | Size | Description |
|  ------- | ---- | --------------------- |
|  `0x0`   | 2    | Index (Starts at 1)   |
|  `0x2`   | 162? | Name                  |
|  `0xA4`  | 1    | Type                  |
|  `0xA6`  | 2    | Length (String only)  |
