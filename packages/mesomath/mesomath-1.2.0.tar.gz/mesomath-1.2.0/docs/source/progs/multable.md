(tutorialmultable)=
# bmultable tutorial

`bmultable` is a simple utility for printing sexagesimal multiplication tables in the style of those that aspiring scribes in ancient Babylon struggled to memorize.

## Running `bmultable`

If you [installed](installation)  `MesoMath` using `pip`, `pipx` or `hatch`, you only have to issue:

    $ bmultable
    usage: bmultable [-h] [-s SEPARATOR] [-p] [-f] mult
    bmultable: error: the following arguments are required: mult
    $ 

The above output indicates that `bmultable` is there, but you haven't told it what to do. You can try also:

    $ python -m mesomath.bmultable

to run `bmultable`.

### Options

    $ bmultable -h
    usage: bmultable [-h] [-s SEPARATOR] [-p] [-f] mult

    Prints Babylonian multiplication tables.

    positional arguments:
    mult                  Multiplier, use 0 for a list of multiplication tables used in scribal learning

    options:
    -h, --help            show this help message and exit
    -s SEPARATOR, --separator SEPARATOR
                            Sexagesimal digit separator (default: :)
    -p, --principal       Use only principal numbers (default: False)
    -f, --fill            Pad with zeros (default: False)

    jccsvq fecit, 2025. Public domain.

### List of tables learned by the scribes

The list comprised only regular numbers and their reciprocals as multipliers... plus the number 7! You can obtain a listing of the tables by issuing:

    $ bmultable 0
    List of multipliers:

    50         1:12
    45         1:20
    44:26:40   1:21
    40         1:30
    36         1:40
    30            2
    25         2:24
    24         2:30
    22:30      2:40
    20            3
    18         3:20
    16:40      3:36
    16         3:45
    15            4
    12:30      4:48
    12            5
    10            6
    9          6:40
    8:20       7:12
    8          7:30
    7:30          8
    7:12       8:20
    7
    6:40          9
    6            10
    5            12
    4:30      13:20
    4            15
    3:45         16
    3:20         18
    3            20
    2:30         24
    2:24         25
    2            30
    1:40         36
    1:30         40
    1:20         45
    1:15         48

### Example

The following prints the multiplication table for sexagesimal number `1:12`. Options `-p --principal` limit multiplicand to the list of *principal numbers*. Without this option the table includes al multiplicands between 1 and 59.

$ bmultable 1:12 -p

     i             i * 1:12 
    =======================
     1                 1:12
     2                 2:24
     3                 3:36
     4                 4:48
     5                  6:0
     6                 7:12
     7                 8:24
     8                 9:36
     9                10:48
    10                 12:0
    11                13:12
    12                14:24
    13                15:36
    14                16:48
    15                 18:0
    16                19:12
    17                20:24
    18                21:36
    19                22:48
    20                 24:0
    30                 36:0
    40                 48:0
    50                1:0:0

With the `-f --fill` option, the sexagesimal digits are padded with zeros if necessary:

    $ bmultable 1:12 -pf

     i             i * 1:12 
    =======================
     1                01:12
     2                02:24
     3                03:36
     4                04:48
     5                06:00
     6                07:12
     7                08:24
     8                09:36
     9                10:48
    10                12:00
    11                13:12
    12                14:24
    13                15:36
    14                16:48
    15                18:00
    16                19:12
    17                20:24
    18                21:36
    19                22:48
    20                24:00
    30                36:00
    40                48:00
    50             01:00:00

Finally, you can also change the sexagesimal digit separator with the `-s --separator` option:


    $ bmultable 1:12 -pfs .

     i             i * 1:12 
    =======================
     1                01.12
     2                02.24
     3                03.36
     4                04.48
     5                06.00
     6                07.12
     7                08.24
     8                09.36
     9                10.48
    10                12.00
    11                13.12
    12                14.24
    13                15.36
    14                16.48
    15                18.00
    16                19.12
    17                20.24
    18                21.36
    19                22.48
    20                24.00
    30                36.00
    40                48.00
    50             01.00.00