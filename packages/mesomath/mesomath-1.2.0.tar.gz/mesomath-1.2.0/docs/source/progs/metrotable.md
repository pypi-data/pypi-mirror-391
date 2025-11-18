<link rel="icon" type="image/svg" href="../favicon.svg">

# `metrotable` tutorial

Jesús Cabrera ([jccsvq](https://jccsvq.github.io/))(*), 2025.

>(*) At gmail.com

## Introduction

Python3 command line application based on [MesoMath](https://github.com/jccsvq/mesomath) for printing fragments of [**metrological tables**](https://cdli.earth/articles/cdlj/2009-1.pdf) in the style of those used by ancient Babylonian scribes and their apprentices.

The metrological tables showed the correspondence between the additive values ​​of measurements of length, surface, weight, etc. and the abstract multiplicative sexagesimal numbers required by multiplicative arithmetic (calculations of areas, volumes, etc.). A modern analogy would be the following: we have a square with a side measuring one yard, two feet, and five inches (the additive measurement), and we want to calculate its area. We would need to convert the measurement to a homogeneous unit, for example, inches, with 65 inches. With this value, we can calculate the area of ​​the square as 65^2 = 4225 square inches. This value of 65 would be our abstract multiplicative number, and a modern metrological table would show us an entry for the association:

    1 yard 2 feet 5 inches -> 65

## Running `metrotable`

If you [installed](installation)  `MesoMath` using `pip`, `pipx` or `hatch`, you only have to issue:

    $ metrotable
    Nothing to do, exiting!
    $ 

The output: "Nothing to do, exiting!" indicates that `metrotable` is there, but you haven't told it what to do. You can try also:

    $ python -m mesomath.metrotable

to run `metrotable`. Let us now try:

    $ metrotable -h

or, if you prefer long options:

    $ metrotable --help

to get a listing of short and long options:

    usage: metrotable [-h] [-t {L,Lh,S,V,C,W,SysG,SysS}] [-m MIN] [-M MAX]
                      [-i INCREMENT] [-w WIDTH] [-f FORCE] [-x {1,2,3,4}] [-n]
                      [-v] [-r] [-p]

    Prints an excerpt of a metrological table

    options:
      -h, --help            show this help message and exit
      -t {L,Lh,S,V,C,W,SysG,SysS}, --type {L,Lh,S,V,C,W,SysG,SysS}
                            Type of metrological table to print (Try: -r for a
                            remainder) (default: None)
      -m MIN, --min MIN     Minimun value of variable to print, ex: "10 susi"
                            (default: 1)
      -M MAX, --max MAX     Maximun value of variable to print, ex:"2 kus", or a
                            comma separated list "2 kus,5 kus" (default: 10)
      -i INCREMENT, --increment INCREMENT
                            Increment of the variable between table lines, ex: "5
                            susi" or a comma separated list matching MAX in length
                            "5 susi,1 kus" (default: 1)
      -w WIDTH, --width WIDTH
                            Sets the reserved width for printing measurement
                            values ​​to WIDTH (default: 20)
      -f FORCE, --force FORCE
                            Force base unit to number FORCE (default: -1)
      -x {1,2,3,4}, --example {1,2,3,4}
                            Runs an example test (default: None)
      -n, --noheader        Suppress header printing (for chaining results)
                            (default: False)
      -v, --verbose         More information in the header and reciprocals if the
                            abstract numbers are regular (default: False)
      -r, --remainder       Lists the available measurement systems and their
                            units, then exits (default: False)
      -F {0,1}, --fractions {0,1}
                            Use fractions, -F 1 to include 1/6 (default: -1)
      -p, --pedantic        Write the coefficients of the units in the
                            measurements using the S and G Systems (default:
                            False)
      -a, --academic        With [-F|--fractions] or [-r|--remainder] uses the academic names of
                            units. (default: False)

    jccsvq fecit, 2025. Public domain.


## How to use

### First steps

Start by:

    $ metrotable -r

to take a look at the metrological systems covered by this application:

    Remainder of systems and units: Old Babylonian Period
    =======================================================
    System L:  Babylonian length meassurements
        Units:  danna <-30- us <-60- ninda <-12- kus <-30- susi
        Base unit:  ninda
    System Lh:  Babylonian length meassurements (Heights)
        Units:  danna <-30- us <-60- ninda <-12- kus <-30- susi
        Base unit:  kus
    System S:  Babylonian surface meassurements
        Units:  gan <-100- sar <-60- gin <-180- se
        Base unit:  gin
    System V:  Babylonian volume meassurements
        Units:  gan <-100- sar <-60- gin <-180- se
        Base unit:  gin
    System C:  Babylonian capacity meassurements
        Units:  gur <-5- bariga <-6- ban <-10- sila <-60- gin <-180- se
        Base unit:  gin
    System W:  Babylonian weight meassurements
        Units:  gu <-60- mana <-60- gin <-180- se
        Base unit:  gin
    NPVN System S:  Babylonian System S to count objects
        Units:  sargal <-6- saru <-10- sar <-6- gesu <-10- ges <-6- u <-10- dis
        Base unit:  dis
    NPVN System G:  Babylonian System G to count objects
        Units:  sargal <-6- saru <-10- sar <-6- buru <-10- bur <-3- ese <-6- iku
        Base unit:  iku

or

    $ metrotable -ra

    Remainder of systems and units: Old Babylonian Period
    =======================================================
    System L:  Babylonian length meassurements
        Units:  danna <-30- UŠ <-60- ninda <-12- kuš3 <-30- šu-si
        Base unit:  ninda
    System Lh:  Babylonian length meassurements (Heights)
        Units:  danna <-30- UŠ <-60- ninda <-12- kuš3 <-30- šu-si
        Base unit:  kus
    System S:  Babylonian surface meassurements
        Units:  GAN2 <-100- sar <-60- gin2 <-180- še
        Base unit:  gin
    System V:  Babylonian volume meassurements
        Units:  GAN2 <-100- sar <-60- gin2 <-180- še
        Base unit:  gin
    System C:  Babylonian capacity meassurements
        Units:  gur <-5- bariga <-6- ban2 <-10- sila3 <-60- gin2 <-180- še
        Base unit:  gin
    System W:  Babylonian weight meassurements
        Units:  gu2 <-60- ma-na <-60- gin2 <-180- še
        Base unit:  gin
    NPVN System S:  Babylonian System S to count objects
        Units:  šar2-gal <-6- šar'u <-10- šar2 <-6- geš'u <-10- geš <-6- u <-10- diš
        Base unit:  dis
    NPVN System G:  Babylonian System G to count objects
        Units:  šar2-gal <-6- šar'u <-10- šar2 <-6- bur'u <-10- bur3 <-3- eše3 <-6- iku
        Base unit:  iku


Most interestingly, here are some examples to get an idea of ​​what the program offers:

    $ metrotable -x 1

    Example 1:
            Table: Babylonian length meassurements
            ubase: 2 (ninda)
            From: 10 susi
            To: 2 kus
            Step by: 5 susi
    Output follows:

    Metrological list for Babylonian length meassurements
    Base unit: ninda

    Meassurement              Abstract
    =========================================
    10 susi               ->  1:40
    15 susi               ->  2:30
    20 susi               ->  3:20
    25 susi               ->  4:10
    1 kus                 ->  5
    1 kus 5 susi          ->  5:50
    1 kus 10 susi         ->  6:40
    1 kus 15 susi         ->  7:30
    1 kus 20 susi         ->  8:20
    1 kus 25 susi         ->  9:10
    2 kus                 ->  10

or with the  `-v` or `--verbose` options to obtain a header with more information and a new column with the reciprocals of the abstract numbers if they are regular or "igi nu" ("not regular" in Sumerian) if thei are not:

    $ metrotable -x 1 -v

    Example 1:
            Table: Babylonian length meassurements
            ubase: 2 (ninda)
            From: 10 susi
            To: 2 kus
            Step by: 5 susi
    Output follows:

    Metrological list for Babylonian length meassurements
      units:  danna <-30- us <-60- ninda <-12- kus <-30- susi
      cfact:  1 30 360 21600 648000
    Base unit: ninda

    Meassurement              Abstract        Reciprocal
    ====================================================
    10 susi               ->  1:40            36
    15 susi               ->  2:30            24
    20 susi               ->  3:20            18
    25 susi               ->  4:10            14:24
    1 kus                 ->  5               12
    1 kus 5 susi          ->  5:50            --igi nu--
    1 kus 10 susi         ->  6:40            9
    1 kus 15 susi         ->  7:30            8
    1 kus 20 susi         ->  8:20            7:12
    1 kus 25 susi         ->  9:10            --igi nu--
    2 kus                 ->  10              6

and, in the same way:

    $ metrotable -x 2 -v

    Example 2:
            Table: Babylonian surface meassurements
            ubase: 2 (sar)
            From: 10 gin
            To: 2 sar
            Step by: 10 gin
    Output follows:

    Metrological list for Babylonian surface meassurements
      units:  gan <-100- sar <-60- gin <-180- se
      cfact:  1 180 10800 1080000
    Base unit: sar
    
    Meassurement              Abstract        Reciprocal
    ====================================================
    10 gin                ->  10              6
    20 gin                ->  20              3
    30 gin                ->  30              2
    40 gin                ->  40              1:30
    50 gin                ->  50              1:12
    1 sar                 ->  1               1
    1 sar 10 gin          ->  1:10            --igi nu--
    1 sar 20 gin          ->  1:20            45
    1 sar 30 gin          ->  1:30            40
    1 sar 40 gin          ->  1:40            36
    1 sar 50 gin          ->  1:50            --igi nu--
    2 sar                 ->  2               30

    $ metrotable -x 3 -v

    Example 3:
            Table: Babylonian capacity meassurements
            ubase: 2 (sila)
            From: 1 gur
            To: 3 gur
            Step by: 3 ban
    Output follows:

    Metrological list for Babylonian capacity meassurements
      units:  gur <-5- bariga <-6- ban <-10- sila <-60- gin <-180- se
      cfact:  1 180 10800 108000 648000 3240000
    Base unit: sila

    Meassurement              Abstract        Reciprocal
    ====================================================
    1 gur                 ->  5               12
    1 gur 3 ban           ->  5:30            --igi nu--
    1 gur 1 bariga        ->  6               10
    1 gur 1 bariga 3 ban  ->  6:30            --igi nu--
    1 gur 2 bariga        ->  7               --igi nu--
    1 gur 2 bariga 3 ban  ->  7:30            8
    1 gur 3 bariga        ->  8               7:30
    1 gur 3 bariga 3 ban  ->  8:30            --igi nu--
    1 gur 4 bariga        ->  9               6:40
    1 gur 4 bariga 3 ban  ->  9:30            --igi nu--
    2 gur                 ->  10              6
    2 gur 3 ban           ->  10:30           --igi nu--
    2 gur 1 bariga        ->  11              --igi nu--
    2 gur 1 bariga 3 ban  ->  11:30           --igi nu--
    2 gur 2 bariga        ->  12              5
    2 gur 2 bariga 3 ban  ->  12:30           4:48
    2 gur 3 bariga        ->  13              --igi nu--
    2 gur 3 bariga 3 ban  ->  13:30           4:26:40
    2 gur 4 bariga        ->  14              --igi nu--
    2 gur 4 bariga 3 ban  ->  14:30           --igi nu--
    3 gur                 ->  15              4

    $ metrotable -x 4 -v

    Example 4:
            Table: Babylonian length meassurements
            ubase: 2 (ninda)
            From: 10 susi
            To: 2 kus,12 kus,5 ninda
            Step by: 5 susi,1 kus,6 kus
    Output follows:

    Metrological list for Babylonian length meassurements
      units:  danna <-30- us <-60- ninda <-12- kus <-30- susi
      cfact:  1 30 360 21600 648000
    Base unit: ninda

    Meassurement              Abstract        Reciprocal
    ====================================================
    10 susi               ->  1:40            36
    15 susi               ->  2:30            24
    20 susi               ->  3:20            18
    25 susi               ->  4:10            14:24
    1 kus                 ->  5               12
    1 kus 5 susi          ->  5:50            --igi nu--
    1 kus 10 susi         ->  6:40            9
    1 kus 15 susi         ->  7:30            8
    1 kus 20 susi         ->  8:20            7:12
    1 kus 25 susi         ->  9:10            --igi nu--
    2 kus                 ->  10              6
    ---------------------------------------------------
    2 kus                 ->  10              6
    3 kus                 ->  15              4
    4 kus                 ->  20              3
    5 kus                 ->  25              2:24
    6 kus                 ->  30              2
    7 kus                 ->  35              --igi nu--
    8 kus                 ->  40              1:30
    9 kus                 ->  45              1:20
    10 kus                ->  50              1:12
    11 kus                ->  55              --igi nu--
    1 ninda               ->  1               1
    ---------------------------------------------------
    1 ninda               ->  1               1
    1 ninda 6 kus         ->  1:30            40
    2 ninda               ->  2               30
    2 ninda 6 kus         ->  2:30            24
    3 ninda               ->  3               20
    3 ninda 6 kus         ->  3:30            --igi nu--
    4 ninda               ->  4               15
    4 ninda 6 kus         ->  4:30            13:20
    5 ninda               ->  5               12

### Defining a metrological table

The program needs four pieces of data to calculate a segment of a metrological table:

* Metrological table type (options `-t` or `--type`)
    * L:   length meassurements
    * Lh:   length meassurements (Heights)
    * S:   surface meassurements
    * V:   volume meassurements
    * C:   capacity meassurements
    * W:   weight meassurements
    * SysS:   System S to count objects
    * SysG:   System G to count objects
*  Starting meassurement value (options `-t` or `--min`)
*  Final meassurement value (options `-M` or `--max`)
*  Meassurement increment between table rows (options `-i` or `--inc`)

For example:

    $ metrotable -t L -m '10 susi' -M '2 kus' -i '5 susi'

will reproduce example 1 (add `-v` at will).

    Metrological list for Babylonian length meassurements
    Base unit: ninda

    Meassurement              Abstract
    =========================================
    10 susi               ->  1:40
    15 susi               ->  2:30
    20 susi               ->  3:20
    25 susi               ->  4:10
    1 kus                 ->  5
    1 kus 5 susi          ->  5:50
    1 kus 10 susi         ->  6:40
    1 kus 15 susi         ->  7:30
    1 kus 20 susi         ->  8:20
    1 kus 25 susi         ->  9:10
    2 kus                 ->  10

###  Using successive increments

We can subdivide the table into different sections with different increments by entering MAX and INC as comma-separated lists. For instance, by using:

    MAX = '2 kus,12 kus,5 ninda'
    INC = '5 susi,1 kus,6 kus'

in

    $ metrotable -t L -m '10 susi' -M '2 kus,12 kus,5 ninda' -i '5 susi,1 kus,6 kus' -v

we obtain the table from 10 susi to 2 kus with increment of 5 susi, from 2 ku to  12 kus (1 ninda) with increment by 1 kus and from this point to 5 ninda by 6 kus:


    Metrological list for Babylonian length meassurements
      units:  danna <-30- us <-60- ninda <-12- kus <-30- susi
      cfact:  1 30 360 21600 648000
    Base unit: ninda

    Meassurement              Abstract        Reciprocal
    ====================================================
    10 susi               ->  1:40            36
    15 susi               ->  2:30            24
    20 susi               ->  3:20            18
    25 susi               ->  4:10            14:24
    1 kus                 ->  5               12
    1 kus 5 susi          ->  5:50            --igi nu--
    1 kus 10 susi         ->  6:40            9
    1 kus 15 susi         ->  7:30            8
    1 kus 20 susi         ->  8:20            7:12
    1 kus 25 susi         ->  9:10            --igi nu--
    2 kus                 ->  10              6
    ---------------------------------------------------
    2 kus                 ->  10              6
    3 kus                 ->  15              4
    4 kus                 ->  20              3
    5 kus                 ->  25              2:24
    6 kus                 ->  30              2
    7 kus                 ->  35              --igi nu--
    8 kus                 ->  40              1:30
    9 kus                 ->  45              1:20
    10 kus                ->  50              1:12
    11 kus                ->  55              --igi nu--
    1 ninda               ->  1               1
    ---------------------------------------------------
    1 ninda               ->  1               1
    1 ninda 6 kus         ->  1:30            40
    2 ninda               ->  2               30
    2 ninda 6 kus         ->  2:30            24
    3 ninda               ->  3               20
    3 ninda 6 kus         ->  3:30            --igi nu--
    4 ninda               ->  4               15
    4 ninda 6 kus         ->  4:30            13:20
    5 ninda               ->  5               12

### Other options

#### Options `-n` `--noheader`  

Suppresses the printing of the table header, which can be useful if you want to join table segments by shell scripting.

    $ metrotable ...  > table.txt
    $ metrotable ... -n >> table.txt
    $ metrotable ... -n >> table.txt
    ...

#### Options `-f` `--force`

It allows the calculation of abstract numbers by forcing any unit as the base unit. For instance:


    $ metrotable -t W -m '1 mana' -M '5 mana' -i '1 mana' 

    Metrological list for Babylonian weight meassurements
    Base unit: gin

    Meassurement              Abstract
    =========================================
    1 mana                ->  1
    2 mana                ->  2
    3 mana                ->  3
    4 mana                ->  4
    5 mana                ->  5

    $ metrotable -t W -m '1 mana' -M '5 mana' -i '1 mana' -f 0

    Metrological list for Babylonian weight meassurements
    Base unit: se

    Meassurement              Abstract
    =========================================
    1 mana                ->  3
    2 mana                ->  6
    3 mana                ->  9
    4 mana                ->  12
    5 mana                ->  15

#### Options `-w`  `--width`

Changes the default of 20 chars width  of the meassurement text field

    $ metrotable -t W -m '1 mana' -M '5 mana' -i '1 mana' -w 30

    Metrological list for Babylonian weight meassurements
    Base unit: gin

    Meassurement                        Abstract
    =========================================
    1 mana                          ->  1
    2 mana                          ->  2
    3 mana                          ->  3
    4 mana                          ->  4
    5 mana                          ->  5

#### Options `-p` `--pedantic`

Will print the coefficients of the units expressed in the system S  (system G for surfaces and volumes) making the output more closely mimic the way the measurements were actually inscribed on the clay tablets, but it complicates things for the modern reader:

    $ metrotable -t L -m '10 susi' -M '2 kus' -i '5 susi' -pv

    Metrological list for Babylonian length meassurements
      units:  danna <-30- us <-60- ninda <-12- kus <-30- susi
      cfact:  1 30 360 21600 648000
    Base unit: ninda

    Meassurement              Abstract        Reciprocal
    ====================================================
    (1 u) susi            ->  1:40            36
    (1 u 5 dis) susi      ->  2:30            24
    (2 u) susi            ->  3:20            18
    (2 u 5 dis) susi      ->  4:10            14:24
    (1 dis) kus           ->  5               12
    (1 dis) kus (5 dis) susi  ->  5:50            --igi nu--
    (1 dis) kus (1 u) susi  ->  6:40            9
    (1 dis) kus (1 u 5 dis) susi  ->  7:30            8
    (1 dis) kus (2 u) susi  ->  8:20            7:12
    (1 dis) kus (2 u 5 dis) susi  ->  9:10            --igi nu--
    (2 dis) kus           ->  10              6


This may distort the output; combine it with `-w`:

    $ metrotable -t L -m '10 susi' -M '2 kus' -i '5 susi' -pvw 30

    Metrological list for Babylonian length meassurements
      units:  danna <-30- us <-60- ninda <-12- kus <-30- susi
      cfact:  1 30 360 21600 648000
    Base unit: ninda

    Meassurement                        Abstract        Reciprocal
    ====================================================
    (1 u) susi                      ->  1:40            36
    (1 u 5 dis) susi                ->  2:30            24
    (2 u) susi                      ->  3:20            18
    (2 u 5 dis) susi                ->  4:10            14:24
    (1 dis) kus                     ->  5               12
    (1 dis) kus (5 dis) susi        ->  5:50            --igi nu--
    (1 dis) kus (1 u) susi          ->  6:40            9
    (1 dis) kus (1 u 5 dis) susi    ->  7:30            8
    (1 dis) kus (2 u) susi          ->  8:20            7:12
    (1 dis) kus (2 u 5 dis) susi    ->  9:10            --igi nu--
    (2 dis) kus                     ->  10              6

#### Option `-F --fractions`

Use the `-F0` option to have the output use the fractions `1/3, 1/2, 2/3, 5/6'`, `-F1` to also include the fraction `1/6`:

    $ metrotable -t L -m '10 susi' -M '2 kus' -i '5 susi'

    Metrological list for Babylonian length meassurements
    Base unit: ninda

    Meassurement              Abstract       
    =========================================
    10 susi               ->  1:40           
    15 susi               ->  2:30           
    20 susi               ->  3:20           
    25 susi               ->  4:10           
    1 kus                 ->  5              
    1 kus 5 susi          ->  5:50           
    1 kus 10 susi         ->  6:40           
    1 kus 15 susi         ->  7:30           
    1 kus 20 susi         ->  8:20           
    1 kus 25 susi         ->  9:10           
    2 kus                 ->  10  
    $           
    $ metrotable -t L -m '10 susi' -M '2 kus' -i '5 susi' -F0

    Metrological list for Babylonian length meassurements
    Base unit: ninda

    Meassurement              Abstract       
    =========================================
    1/3 kus               ->  1:40           
    1/2 kus               ->  2:30           
    2/3 kus               ->  3:20           
    5/6 kus               ->  4:10           
    1 kus                 ->  5              
    1 kus 5 susi          ->  5:50           
    1 1/3 kus             ->  6:40           
    1 1/2 kus             ->  7:30           
    1 2/3 kus             ->  8:20           
    1 5/6 kus             ->  9:10           
    2 kus                 ->  10     
    $        
    $ metrotable -t L -m '10 susi' -M '2 kus' -i '5 susi' -F1

    Metrological list for Babylonian length meassurements
    Base unit: ninda

    Meassurement              Abstract       
    =========================================
    1/3 kus               ->  1:40           
    1/2 kus               ->  2:30           
    2/3 kus               ->  3:20           
    5/6 kus               ->  4:10           
    1 kus                 ->  5              
    1 1/6 kus             ->  5:50           
    1 1/3 kus             ->  6:40           
    1 1/2 kus             ->  7:30           
    1 2/3 kus             ->  8:20           
    1 5/6 kus             ->  9:10           
    1/6 ninda             ->  10  
    $

You may combine it with `-p` (pedantic mode):

    $ metrotable -t L -m '10 susi' -M '2 kus' -i '5 susi' -pF0

    Metrological list for Babylonian length meassurements
    Base unit: ninda

    Meassurement              Abstract       
    =========================================
    1/3 kus               ->  1:40           
    1/2 kus               ->  2:30           
    2/3 kus               ->  3:20           
    5/6 kus               ->  4:10           
    (1 dis) kus           ->  5              
    (1 dis) kus (5 dis) susi  ->  5:50           
    (1 dis) 1/3 kus       ->  6:40           
    (1 dis) 1/2 kus       ->  7:30           
    (1 dis) 2/3 kus       ->  8:20           
    (1 dis) 5/6 kus       ->  9:10           
    (2 dis) kus           ->  10             
    $
    $ metrotable -t L -m '10 susi' -M '2 kus' -i '5 susi' -pF1

    Metrological list for Babylonian length meassurements
    Base unit: ninda

    Meassurement              Abstract       
    =========================================
    1/3 kus               ->  1:40           
    1/2 kus               ->  2:30           
    2/3 kus               ->  3:20           
    5/6 kus               ->  4:10           
    (1 dis) kus           ->  5              
    (1 dis) 1/6 kus       ->  5:50           
    (1 dis) 1/3 kus       ->  6:40           
    (1 dis) 1/2 kus       ->  7:30           
    (1 dis) 2/3 kus       ->  8:20           
    (1 dis) 5/6 kus       ->  9:10           
    1/6 ninda             ->  10  
    $

#### Options `-a --academic`

You can combine the `-F --fractions` options with `-a --academic` to obtain listings using the academic names of the units:

    $ metrotable -x 1 -aF1 -f0 -v

    Example 1:
            Table: Babylonian length meassurements
            ubase: 0 (šu-si)
            From: 10 susi
            To: 2 kus
            Step by: 5 susi
    Output follows:

    Metrological list for Babylonian length meassurements
      units:  danna <-30- UŠ <-60- ninda <-12- kuš3 <-30- šu-si
      cfact:  1 30 360 21600 648000
    Base unit: šu-si

    Meassurement              Abstract        Reciprocal
    ====================================================
    1/3 kuš3              ->  10              6
    1/2 kuš3              ->  15              4
    2/3 kuš3              ->  20              3
    5/6 kuš3              ->  25              2:24
    1 kuš3                ->  30              2
    1 1/6 kuš3            ->  35              --igi nu--
    1 1/3 kuš3            ->  40              1:30
    1 1/2 kuš3            ->  45              1:20
    1 2/3 kuš3            ->  50              1:12
    1 5/6 kuš3            ->  55              --igi nu--
    1/6 ninda             ->  1               1
