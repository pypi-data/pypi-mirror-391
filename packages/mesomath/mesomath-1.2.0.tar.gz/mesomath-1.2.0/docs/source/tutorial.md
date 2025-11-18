(tutorialmesomath)=
# MesoMath ``v1.2.0`` Tutorial

![mesomath](_static/mesomath.png)


Jesús Cabrera ([jccsvq](https://jccsvq.github.io/))(*), 2025.

>(*) At gmail.com

## Introduction

MesoMath is a `Python3` package intended for the arithmetic of natural sexagesimal numbers, mainly in their "**floating**" aspect (i.e. eliminating all possible trailing sexagesimal zeros on the right, thus abstracting from the order of magnitude of the quantity expressed), as performed by the Babylonian scribes and their apprentices in ancient times. It also allows to deal with the basic aspects of metrology of the time.

Inpired by the arithmetic and metrological parts of Baptiste Mélès' [MesoCalc](https://github.com/BapMel/mesocalc), it aims to bring this type of calculation to `Python` programming (see the [API documentation](mesomathpackage)) and to the command line as an efficient and versalite calculator as you will see along this tutorial.

## `babcalc`: Running MesoMath as a Mesopotamian/Babylonian calculator

If you [installed](installation)  `MesoMath` using `pip`, `pipx` or `hatch`, you only have to issue:

    $ babcalc

    Welcome to Babylonian Calculator 1.2.0
        ...the calculator that every scribe should have!

    Use: bn(number) for sexagesimal calculations
    Metrological classes: bl, bs, bv, bc, bw, bG, bS and bb loaded.
    Use exit() or Ctrl-D (i.e. EOF) to exit

    --> 

to enter an interactive `Python` interpreter with all relevant `mesomath` classes loaded. Otherwise, you will need to import them individually:

    $ python3
    Python 3.11.2 (main, Apr 28 2025, 14:11:48) [GCC 12.2.0] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> 
    >>> from mesomath.babn import BabN as bn
    >>> from mesomath.npvs import Blen as bl
    >>> from mesomath.npvs import Bsur as bs
    >>> from mesomath.npvs import Bvol as bv
    >>> from mesomath.npvs import Bcap as bc
    >>> from mesomath.npvs import Bwei as bw
    >>> from mesomath.npvs import BsyG as bG
    >>> from mesomath.npvs import BsyS as bS
    >>> from mesomath.npvs import Bbri as bb
    >>> ...

You can also try:

    $ python -m mesomath.babcalc


## Hands on

In what follows, the reader is assumed to be familiar with the key topics of Mesopotamian mathematics, in particular with the concepts of **decimal** and **sexagesimal** notations, **absolute** and **floating** numbers and with the concepts of **regular** and **reciprocal** numbers.

### First steps

#### Introducing or creating Babylonian numbers

Let us create our first Babylonian number 

    --> a = bn(405)
    --> 

`bn(405)` creates it and it is asigned to variable `a`. Let us explore some of its properties:

    --> a.dec
    405
    --> int(a)
    405
    --> a.list
    [6, 45]
    --> a.factors
    (0, 4, 1, 1)
    --> a
    6:45
    --> a.isreg
    True

* `a.dec` This is the decimal expansion of the number, we have used it for its creation above
* `a.list`This is the list of sexagesimal digits of the number
* `a.factors` This is the list of factors/divisors of the number (see bellow)
*  `a` or `print(a)` give us the printable representation of the sexagesimal number `6:45`
*  `a.isreg` This tells us that it is a "regular" number

We can obtain all this information together using:

    --> a.explain()
    |  Sexagesimal number: [6, 45] is the decimal number: 405.
    |    It may be written as (2^0 * 3^4 * 5^1 * 1),
    |    so, it is a regular number with reciprocal: 8:53:20
    >>>

while for a non-regular number:

    --> b=bn(7)
    --> b.isreg
    False
    --> b.explain()
    |  Sexagesimal number: [7] is the decimal number:   7.
    |    It may be written as (2^0 * 3^0 * 5^0 * 7),
    |    so, it is NOT a regular number and has NO  reciprocal.
    |    but an approximate inverse is: 8:34:17:9
    |    and a close regular is: 6:59:54:14:24
    |    whose reciprocal is: 8:34:24:11:51:6:40
    --> 


>Any natural number n can be writen as `n = 2^i × 3^j × 5^k × l` where  `i, j, k, l  ≥ 0`, `i, j, k` are the powers of `2, 3` and `5`, and `l` is a "remainder" that should not be divisible by `2, 3` and `5`. The tuple  `(i,j,k,l)` is what `a.factors` returned above.

We can introduce bab numbers in  four ways:

*  using the decimal equivalent: `a=bn(405)`
*  using the list of  sexagesimal digits: `a=bn([6,45])`
*  using its string or literal expression: `a=bn('6:45')` or `a=bn("6.45")`
*  using its factors as a tuple, as  405 = 2^0 * 3^4 * 5^1 * 1,  `a=bn((0,4,1,1))`

so we have:

    --> b = bn([6,45])
    --> c = bn('6:45')
    --> d = bn((0,4,1,1))
    --> a == b == c == d
    True
    --> 


>**_NOTE:_**  The `BabN` class is for non-negative integers. By design, if you enter `a=bn(-405)`, you get the same result as with `a=bn(405)`.

The printable or string representation of numbers uses colon `:``as separator  by default.

    --> n1=bn(314159265)
    --> n1
    24:14:26:27:45
    --> 

You can change this default to your liking:

    --> bn.sep = '.'
    --> n1
    24.14.26.27.45
    --> bn.sep = '-'
    --> n1
    24-14-26-27-45
    --> bn.sep = '<>'
    --> n1
    24<>14<>26<>27<>45
    --> 

but you can only use  `:` and `.` for input:

    --> m = bn('3:14:16')
    --> m1 = bn('3.14.16')
    --> print(m,m1)
    3:14:16 3:14:16
    --> 

You can obtain the number of sexagesimal digits using:

    --> m.len()
    3
    -->

or using the standard `Python` function `len`

    --> len(m)
    3
    --> 

###  Basic arithmetic

#### Addition

We use the addition operator `+` to perform addition:

    --> a = bn('16.24.35')
    --> b = bn('1.33.54.22')
    --> a+b
    1:50:18:57
    --> 

addition is always absolute:

    --> a = bn('15.42.37.0.0')
    --> b = bn('24.34.0.0.0')
    --> c = a + b
    --> c
    40:16:37:0:0
    --> 

At any time, if we want the floating version of a number, we will use the `float()` method or its synonym `f()`

    --> c.float()
    40:16:37
    --> c.f()
    40:16:37
    --> 

no need to use variables:

    --> bn(45689) + bn(325874)
    1:43:12:43

and finally, integers can be added directly:

    --> bn('33.14.22') + 34
    33:14:56
    --> 5523 + bn('33.14.22')
    34:46:25
    --> 

Of course, we are not limited to two addends:

    --> a + b + bn('33.14.22') + 34
    40:17:10:14:56
    >>>

#### Subtraction

Subtraction, like addition, always gives absolute (not floating) results. It also returns the absolute difference of numbers. This is by design, because Mesopotamian mathematics lacked negative numbers and to save us from mistakes. Thus, subtraction in this application is a commutative operation.

    --> bn(45689) - bn(325874)
    1:17:49:45
    --> bn(325874) - bn(45689)
    1:17:49:45
    --> 

#### Multiplication

Multiplication is absolute by default:

    --> a = bn('34:59:31:12')
    --> b = bn('14:3:45')
    --> a*b
    8:12:4:30:0:0:0

if we want a floating result:

    --> (a*b).f()
    8:12:4:30

or we can change the default

    --> bn.floatmult = True
    --> a*b
    8:12:4:30
    --> 

and restore it again:

    --> bn.floatmult = False
    --> a*b
    8:12:4:30:0:0:0
    --> 


#### Powers

Use the `**` operator:

    --> a
    34:59:31:12
    --> a**2
    20:24:26:24:13:49:26:24
    --> a**3
    11:54:5:36:24:11:24:33:52:7:40:48
    --> 

#### Division

Class `BabN` has two types of division defined, both are floating:

*  **`a/b`** Approximate floating division of two arbitrary numbers. This is the translation of our modern division into the world of Babylonian floating numbers, although we have no evidence that they knew it.
*  **`a//b`** This is the "Babylonian Division", that is, the product of `a` by the reciprocal of `b`, which implies that `b` has to be regular.

Let us try:

    --> a = bn('14.15.16')
    --> b = bn('12.2')
    --> q = a/b
    --> q
    1:11:4:29:15:7:29

now, as a check:

    --> b*q
    14:15:16:0:0:0:2:58
    >>>
a value that, in the world of floating numbers, is very similar to `a`.

We can change the number of digits in the result (approximately, sorry):

    --> bn.rdigits = 10
    --> a/b
    1:11:4:29:15:7:28:45:12:29:52
    --> 



    --> a//b
    Divisor is not a regular number!
    --> b = bn(405)
    --> b
    6:45
    --> b.isreg
    True              # b is regular
    --> c = b.rec()   # c is the reciprocal of b
    --> a//b
    2:6:42:22:13:20
    --> a * c
    2:6:42:22:13:20
    --> c
    8:53:20
    >>>

### Roots

#### Square root

Method .sqrt() returns the floating square root of the numbers.

    --> bn.rdigits = 6
    --> bn(2).sqrt()
    1:24:51:10:7:46
    --> 

Let us check it:

    --> bn(2).sqrt() ** 2
    1:59:59:59:59:59:42:48:20:19:16
    >>>

Let us round it to 6 digits:

    --> (bn(2).sqrt() ** 2).round(6)
    2:0:0:0:0:0
    >>>

and floating it:

    --> (bn(2).sqrt() ** 2).round(6).f()
    2
    --> 

We see that effectively 1:24:51:10:7:46 is an approximation of the square root of 2. To relate this sexagesimal floating value to the square root of two in the decimal system, let's calculate:

    --> (bn(2).sqrt()).dec/60.**5
    1.4142135622427983
    >>>

which is similar to:

    --> from math import sqrt
    --> sqrt(2)
    1.4142135623730951
    >>>

Compare the following result:

    --> (30*bn(2).sqrt()).float()
    42:25:35
    --> 

to the one appearing in tablet [YBC 7289](https://en.wikipedia.org/wiki/YBC_7289)

<a target = "_blank" title="Urcia, A., Yale Peabody Museum of Natural History,  http://peabody.yale.edu, http://hdl.handle.net/10079/8931zqj
derivative work, user:Theodor Langhorne Franklin, CC0, via Wikimedia Commons" href="https://commons.wikimedia.org/wiki/File:YBC-7289-OBV-labeled.jpg"><img width="256" alt="Labeled photograph of YBC 7289 identifying inscribed numbers" src="https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/YBC-7289-OBV-labeled.jpg/256px-YBC-7289-OBV-labeled.jpg?20190204183004"></a>

#### Cube root

Method .cbrt() returns the floating cube root of the numbers.

    --> bn(2).cbrt()
    1:15:35:43
    --> bn(2).cbrt() ** 3
    2:0:0:0:15:12:26:47:50:7
    --> 

etc.

### Complex expressions

The Python engine is behind the scenes, which means we can combine elementary operations to build complex expressions:

    --> a = bn('16.22')
    --> b = bn('44.16')
    --> c = bn('6.45')
    --> d = ((a+b)*(a-b))//c**2
    --> d
    37:7:42:48:53:20
    --> 

use lists:

    --> ll=[a,b,c,d]
    --> ll
    [16:22, 44:16, 6:45, 37:7:42:48:53:20]
    --> min(ll)
    6:45
    --> max(ll)
    37:7:42:48:53:20
    --> 

etc.

### Logical operators

Logical operators are available and can be combined with integers. This can be useful in programming.

    --> a <= b and c.isreg
    True
    --> a < 300
    False


### Other BabN class  attribute

`bn.fill` is set to `False` by default. You can change it to modify the aspect of the printed sexagesimal numbers by adding a left 0 to digits from 0 to 9 i.e. to conver them to 00, 01, ..., 09:

    --> z = bn('1.2.0.14.5.4.3')
    --> z
    1:2:0:14:5:4:3
    --> bn.fill = True
    --> z
    01:02:00:14:05:04:03
    --> bn.fill = False
    --> z
    1:2:0:14:5:4:3
    --> 


### Other BabN class methods

Still to be documented. In the meantime, you can consult Appendix B for help on the `BabB` class (called **`bn`** in this tutorial because we used: `from mesomath.babn import BabN as` **`bn`**).

#### .rec()

This method returns the reciprocal of regular numbers, `None` for non-regular numbers:

    --> a=bn(400)
    --> a
    6:40
    --> a.rec()
    9
    --> a * a.rec()
    1:0:0
    --> b=bn(406)
    --> b
    6:46
    --> b.rec()
    Not regular!
    --> x = b.rec()
    Not regular!
    --> x
    --> type(x)
    <class 'NoneType'>


#### .inv(n)

This is a replacement for .rec() for irregular numbers. Irregular numbers can be said to have infinite-digit reciprocals; this method calculates the first `n` of them.

    --> b=bn(406)
    --> b
    6:46
    --> b.isreg
    False
    --> c=b.inv()
    --> c
    8:52:1:11
    --> b * c
    1:0:0:0:0:26
    --> c=b.inv(10)
    --> c
    8:52:1:10:56:9:27:29:15:44
    --> b * c
    1:0:0:0:0:0:0:0:0:0:27:44
    --> 


#### .round(n)

Returns the first n sexagesimal digits of the number with rounding:

    --> c
    8:52:1:10:56:9:27:29:15:44
    --> c.round(4)
    8:52:1:11
    --> 


Useful when working with approximate floating numbers. Alternatively, you can use the standard function `round`

    --> round(c,4)
    8:52:1:11
    --> 


#### .head(n)

Returns the first n sexagesimal digits of the number without rounding:

    8:52:1:10:56:9:27:29:15:44
    --> c.round(4)
    8:52:1:11
    --> c.head()  # Without argument, returns the first digit only.
    8
    --> c.head(3)
    8:52:1
    --> c.head(7)
    8:52:1:10:56:9:27
    --> 

You will find this method and the next one used in the `example-melville.py` file in your installation directory.

#### .tail(n)

Returns the last n sexagesimal digits of the number:

    --> c
    8:52:1:10:56:9:27:29:15:44
    --> c.tail()   # Without argument, returns the last digit only.
    44
    --> c.tail(2)
    15:44
    --> c.tail(6)
    56:9:27:29:15:44
    >>>

#### .dist(n)

This was not intended for interactive use.

#### .searchreg(minn, maxn, limdigits=6, prt=False)

Searches the `bn.database` database for the closest regular number to the object's.
minn and maxn: must be sexagesimal strings using ":" separator. limdigits max value is 20.

    --> c
    8:52:1:10:56:9:27:29:15:44
    --> c.searchreg('01', '59')
    8:51:26:27:36
    --> c.searchreg('01', '59', 7)
    8:51:26:27:36
    --> c.searchreg('01', '59', 9)
    8:51:26:27:36
    --> c.searchreg('01', '59', 19)
    8:52:2:27:52:35:29:35:23:26:15
    --> bn(7).searchreg('06:40', '07:40', 4, True)
            72000 06:40
            54000 06:45
            37440 06:49:36
            35775 06:50:03:45
            19008 06:54:43:12
            12000 06:56:40
             6750 07:01:52:30
            24000 07:06:40
            43200 07:12
            50500 07:14:01:40
            60864 07:16:54:24
            62640 07:17:24
            82323 07:22:52:03
            88000 07:24:26:40
           108000 07:30
           126400 07:35:06:40
           128250 07:35:37:30
    Minimal distance: 6750, closest regular is: 07:01:52:30
    7:1:52:30
    >>>

### Metrology

#### Basics

In the following, it is assumed that your startup script contains the lines:

    from mesomath.babn import BabN as bn
    from mesomath.npvs import Blen as bl
    from mesomath.npvs import Bsur as bs
    from mesomath.npvs import Bvol as bv
    from mesomath.npvs import Bcap as bc
    from mesomath.npvs import Bwei as bw
    from mesomath.npvs import BsyG as bG
    from mesomath.npvs import BsyS as bS
    from mesomath.npvs import Bbri as bb

so that we can access the classes `BabN, Blen, Bsur,`... using the shorter aliases `bn, bl, bs,` etc. If you are using `babcalc`, this has already been done for you automatically.

This is what the classes `bl`, `bs`, `bv`, `bc`, `bw`, `bG`, `bS` and `ba` represent:

    class  bl: Babylonian length system:
               danna <-30- UŠ <-60- ninda <-12- kuš3 <-30- šu-si

    class  bs: Babylonian surface system:
               GAN2 <-100- sar <-60- gin2 <-180- še

    class  bv: Babylonian volume system:
               GAN2 <-100- sar <-60- gin2 <-180- še

    class  bc: Babylonian capacity system:
               gur <-5- bariga <-6- ban2 <-10- sila3 <-60- gin2 <-180- še

    class  bw: Babylonian weight system:
               gu2 <-60- ma-na <-60- gin2 <-180- še

    class  bG: Babylonian counting System G:
               šar2-gal <-6- šar'u <-10- šar2 <-6- bur'u <-10- bur3 <-3- eše3 <-6- iku

    class  bS: Babylonian counting System S:
               šar2-gal <-6- šar'u <-10- šar2 <-6- geš'u <-10- geš <-6- u <-10- diš

    Class  bb: Babylonian brick counting system:
               GAN2 <-100- sar <-60- gin2 <-180- še

However, for ease of writing, the real or academic names of the units in these metrological systems have been simplified by removing capital letters, numbers, hyphens, and diacritics. Therefore, for inputting measurements, we will use the following unit names:

Class|Metrology|Units
-----|---------|-----
bl| Babylonian length system|  susi, kus, ninda, us, danna
bs| Babylonian surface system|  se, gin, sar, gan
bv| Babylonian volume system|  se, gin, sar, gan
bc| Babylonian capacity system|  se, gin, sila, ban, bariga, gur
bw| Babylonian weight system|  se, gin, mana, gu
bG| Babylonian System G|  iku, ese, bur, buru, sar, saru, sargal
bS| Babylonian System S|  dis, u, ges, gesu, sar, saru, sargal
bb| Babylonian brick counting system|  se gin sar gan

>Note that scribes wrote volumes as an equivalent surface area multiplied by a standard height of 1 kus; thus, they used the same metrology for surfaces and volumes. Here, however, two different classes will be used, so that one can multiply a surface area by a length to obtain a volume, but one cannot multiply a volume by a length to obtain a four-dimensional volume, which was probably beyond the scribes' understanding.

At any time, you can review the names of the units in each system and their factors through the following, e.g., for capacities:

    --> bc.uname
    ['se', 'gin', 'sila', 'ban', 'bariga', 'gur']
    --> bc.ufact
    [180, 60, 10, 6, 5]
    --> 

and the academic names:

    --> bc.aname
    ['še', 'gin2', 'sila3', 'ban2', 'bariga', 'gur']

or

    --> print(*bc.scheme(bc))
    gur <-5- bariga <-6- ban <-10- sila <-60- gin <-180- se
    --> print(*bc.scheme(bc,1))
    gur <-5- bariga <-6- ban2 <-10- sila3 <-60- gin2 <-180- še
    >>>

In a similar way to what we saw for sexagesimal numbers with the `bn` class. We can introduce measurements in two different ways:

    --> a = bl(11111)
    --> a
    30 ninda 10 kus 11 susi
    --> b = bl('5 ninda 25 susi')
    --> b
    5 ninda 25 susi

In the first case, `a` is defined as a certain (integer) number of times the smallest unit ("susi" in the case of lengths). In the second case, we define the value for `b` textually. Note that we can only use integer values ​​in both cases. Both input methods are available for all classes.

>In fact, there is a **third** entry method that will be seen at the end of this section.

Once you have defined measurements, you can "explain" them:

    --> a.explain()
    This is a Babylonian length meassurement: 30 ninda 10 kus 11 susi
        Metrology:  danna <-30- us <-60- ninda <-12- kus <-30- susi
        Factor with unit 'susi':  1 30 360 21600 648000
    Meassurement in terms of the smallest unit: 11111 (susi)
    Sexagesimal floating value of the above: 3:5:11
    Approximate SI value: 185.18333333333334 meters
    --> 
    --> b.explain()
    This is a Babylonian length meassurement: 5 ninda 25 susi
        Metrology:  danna <-30- us <-60- ninda <-12- kus <-30- susi
        Factor with unit 'susi':  1 30 360 21600 648000
    Meassurement in terms of the smallest unit: 1825 (susi)
    Sexagesimal floating value of the above: 30:25
    Approximate SI value: 30.416666666666668 meters
    --> 

That will give us information about the nature of the measurement and the properties of the measurement system being used.

Note that the value given as "Sexagesimal floating value of the above:" is generated by the `.sex()` method; however, this method accepts a numeric parameter to indicate the unit relative to which this sexagesimal floating value is calculated. This parameter defaults to zero, indicating the first unit in the list provided by `.explain()`: `Unit names: ['susi', 'kus', 'ninda', 'us', 'danna']`

    --> a.sex()   # susi as the base unit
    3:5:11
    --> a.sex(0)  # the same as .sex()
    3:5:11
    --> a.sex(1)  # kus as the base unit
    6:10:22
    --> a.sex(2)  # ninda as the base unit
    30:51:50
    --> a.sex(3)  # us as the base unit
    30:51:50
    --> a.sex(4)  # danna as the base unit
    1:1:43:40
    --> 

This will be useful if you intend to recreate **Metrological lists**. For example, code:

    from mesomath.npvs import Blen as bl

    ls =[]
    for i in range(1,10):
        ls.append(str(i)+' susi')
    for i in '10 15 20 25'.split():
        ls.append(i+' susi')
    ls.append('1 kus')
    for i in '10 15 20 25'.split():
        ls.append('1 kus '+i+' susi')
    ls.append('2 kus')
    for i in ls:
        x=bl(i)
        print(f'{str(x).ljust(15)} -> {str(x.sex(2)).rjust(6)}')



will print this excerpt of the metrological table for length using ninda (x.sex(2)) as base unit:

    1 susi          ->     10
    2 susi          ->     20
    3 susi          ->     30
    4 susi          ->     40
    5 susi          ->     50
    6 susi          ->      1
    7 susi          ->   1:10
    8 susi          ->   1:20
    9 susi          ->   1:30
    10 susi         ->   1:40
    15 susi         ->   2:30
    20 susi         ->   3:20
    25 susi         ->   4:10
    1 kus           ->      5
    1 kus 10 susi   ->   6:40
    1 kus 15 susi   ->   7:30
    1 kus 20 susi   ->   8:20
    1 kus 25 susi   ->   9:10
    2 kus           ->     10

(See page 8 of [Floating calculation in Mesopotamia](https://hal.science/hal-01515645v2/document) by Christine Proust).

> The `metrotable.py` tool, which specializes in printing segments of metrological tables, is located in the `progs` subdirectory of this package. It also includes its own [tutorial](https://jccsvq.github.io/mesomath/progs/metrotable.html).
>
>The `mtlookup.py` tool in the `progs` subdirectory simulates direct and inverse searches in metrological tables. It also includes its own [tutorial](https://jccsvq.github.io/mesomath/progs/mtlookup.html).
>

Since version v1.1.0 you can get the metrological value of an object directly using the `.metval()` method:

    --> bl('1 kus 15 susi').metval()
    7:30
    >>>


#### Operations

For objects of the same class, the following operations are available:

* Addition
* Subtraction (returns the absolute value of the difference)
* Multiplication by a number
* Division by a number
* Logical operations

Let's look at some examples:


    --> a >= b
    True
    --> a+b
    35 ninda 11 kus 6 susi
    --> a-b
    25 ninda 9 kus 16 susi
    --> b-a                   # a-b == b-a !!!
    --> a-b == b-a
    True
    25 ninda 9 kus 16 susi
    --> 2*a
    1 us 1 ninda 8 kus 22 susi
    --> b*2
    10 ninda 1 kus 20 susi
    --> b*2.5
    12 ninda 8 kus 2 susi
    --> a/2
    15 ninda 5 kus 6 susi
    --> (a+2*b)/5
    8 ninda 2 kus 12 susi
    --> (a+2*b)/5.3
    7 ninda 8 kus 25 susi
    >>>

Additionally, for length measurements we can multiply them together to obtain surfaces and volumes, and for surfaces we can multiply them by lengths to obtain volumes:

    --> c = bl('2 kus')
    --> c
    2 kus
    --> s=a*b
    --> s
    1 gan 56 sar 27 gin 138 se
    --> s.explain()
    This is a Babylonian surface meassurement: 1 gan 56 sar 27 gin 138 se
        Metrology:  gan <-100- sar <-60- gin <-180- se
        Factor with unit 'se':  1 180 10800 1080000
    Meassurement in terms of the smallest unit: 1689798 (se)
    Sexagesimal floating value of the above: 7:49:23:18
    Approximate SI value: 5632.66 square meters
    --> v=s*c
    --> v
    3 gan 12 sar 55 gin 96 se
    --> v.explain()
    This is a Babylonian volume meassurement: 3 gan 12 sar 55 gin 96 se
        Metrology:  gan <-100- sar <-60- gin <-180- se
        Factor with unit 'se':  1 180 10800 1080000
    Meassurement in terms of the smallest unit: 3379596 (se)
    Sexagesimal floating value of the above: 15:38:46:36
    Approximate SI value: 5632.66 cube meters

    --> v2=a*b*c
    --> v2 == v
    True
    --> 

#### Systems S and G

Finally, in cases like this:

    --> a = bv('128 gan')
    --> a
    128 gan
    >>>

we might prefer to see the coefficients of the units expressed in the S system (G system for surfaces and volumes), to do this:

    --> bv.prtsex=True
    --> a
    (7 bur 2 iku) gan
    >>>

This changes the default for objects of the `bv` class and makes the output more closely mimic the way the measurements were actually inscribed on the clay tablets, but it complicates things for the modern reader:

    --> a = bv('128 gan 133 se')
    --> a
    (7 bur 2 iku) gan (2 ges 1 u 3 dis) se
    >>>

If you want this to be the default for all classes, add:

    from mesomath.npvs import MesoM
    MesoM.prtsex = True

to your `initmm.py` file or initiation script.

The third input method cited above makes use of these types of strings; in fact, the parentheses have been introduced to make them easier to parse as input:

    --> b = bv('460800 gan 44 sar 20 gin')
    --> b
    (7 sargal 6 sar 4 buru) gan (4 u 4 dis) sar (2 u) gin
    --> c = bv('(7 sargal 6 sar 4 buru) gan (4 u 4 dis) sar (2 u) gin')
    --> c
    (7 sargal 6 sar 4 buru) gan (4 u 4 dis) sar (2 u) gin
    --> bv.prtsex = False
    --> c
    460800 gan 44 sar 20 gin
    >>>

#### Fractions

There is also basic support for entering *principal fractions*: `1/6, 1/3, 1/2, 2/3, 5/6` (and only for them), thei can be entered in several ways:

    --> a=bl('0+1/3 ninda')
    --> a
    4 kus
    --> a=bl('+1/3 ninda')
    --> a
    4 kus
    --> a=bl('1/3 ninda')
    --> a
    4 kus
    --> a=bl('2 + 1/3 ninda')
    --> a
    2 ninda 4 kus
    --> a=bl('2 1/3 ninda')
    --> a
    2 ninda 4 kus
    --> a=bl('21/3 ninda')
    --> a
    2 ninda 4 kus



For output using `1/3, 1/2, 2/3, 5/6` fractions, you can use the `.prtf()` method:

    --> a=bl(11223344)
    --> a
    17 danna 9 us 35 ninda 11 kus 14 susi
    --> a.prtf()
    '17 danna 9 1/2 us 5 5/6 ninda 1 1/3 kus 4 susi'
    >>>

and if you wish also include  `1/6`:

    --> a.prtf(1)
    '17 1/6 danna 4 1/2 us 5 5/6 ninda 1 1/3 kus 4 susi'
    >>>

If you activate `prtsex` you get:

    --> bl.prtsex=True
    --> a.prtf()
    '(1 u 7 dis) danna (9 dis) 1/2 us (5 dis) 5/6 ninda (1 dis) 1/3 kus (4 dis) susi'
    --> a.prtf(1)
    '(1 u 7 dis) 1/6 danna (4 dis) 1/2 us (5 dis) 5/6 ninda (1 dis) 1/3 kus (4 dis) susi'
    >>>

These results can be used for input:

    --> bl.prtsex=0
    --> b=bl('(1 u 7 dis) 1/6 danna (4 dis) 1/2 us (5 dis) 5/6 ninda (1 dis) 1/3 kus (4 dis) susi')
    --> b
    17 danna 9 us 35 ninda 11 kus 14 susi
    --> b.prtf()
    '17 danna 9 1/2 us 5 5/6 ninda 1 1/3 kus 4 susi'
    --> b.prtf(1)
    '17 1/6 danna 4 1/2 us 5 5/6 ninda 1 1/3 kus 4 susi'
    --> b.dec
    11223344
    --> c=bl(a.prtf(1))
    --> c.dec
    11223344
    >>>

#### Academic names

Since v1.1.0, the .prtf() method has a second switch that allows the academic unit names to be used in the output:

    --> a=bl(11223344)
    --> a.prtf()
    '17 danna 9 1/2 us 5 5/6 ninda 1 1/3 kus 4 susi'
    --> a.prtf(1)
    '17 1/6 danna 4 1/2 us 5 5/6 ninda 1 1/3 kus 4 susi'
    --> a.prtf(1,1)
    '17 1/6 danna 4 1/2 UŠ 5 5/6 ninda 1 1/3 kuš3 4 šu-si'
    --> bl.prtsex=True
    --> a.prtf(0,1)
    '(1 u 7 dis) danna (9 dis) 1/2 UŠ (5 dis) 5/6 ninda (1 dis) 1/3 kuš3 (4 dis) šu-si'
    --> a.prtf(1,1)
    '(1 u 7 dis) 1/6 danna (4 dis) 1/2 UŠ (5 dis) 5/6 ninda (1 dis) 1/3 kuš3 (4 dis) šu-si'
    >>>

This kind of string can also be used as input:

    --> b=bl('(1 u 7 dis) 1/6 danna (4 dis) 1/2 UŠ (5 dis) 5/6 ninda (1 dis) 1/3 kuš3 (4 dis) šu-si')
    --> b.dec
    11223344
    >>>

equivalent to:

    --> b=bl(a.prtf(1,1))
    --> b.dec
    11223344
    >>>

#### Volume vs. Capacity

There were two systems for measuring volume: **capacities**, used to measure grain, beer, and other types of food and goods, and **volume** proper, used to measure everything else. Here, they are represented by the metrological classes `Bcap` (imported here as `bc`) and `Bvol` (`bv`), respectively. Since they are two systems for measuring the same physical quantity, we can convert quantities from one system to the other with the methods `.cap()` and `.vol()`:

    --> a = bv('1 gin')
    --> a.explain()
    This is a Babylonian volume meassurement: 1 gin
        Metrology:  gan <-100- sar <-60- gin <-180- se
        Factor with unit 'se':  1 180 10800 1080000
    Meassurement in terms of the smallest unit: 180 (se)
    Sexagesimal floating value of the above: 3
    Approximate SI value: 0.3 cube meters
    --> b = a.cap()
    --> b.explain()
    This is a Babylonian capacity meassurement: 1 gur
        Metrology:  gur <-5- bariga <-6- ban <-10- sila <-60- gin <-180- se
        Factor with unit 'se':  1 180 10800 108000 648000 3240000
    Meassurement in terms of the smallest unit: 3240000 (se)
    Sexagesimal floating value of the above: 15
    Approximate SI value: 300.0 litres
    --> (b.vol()).explain()
    This is a Babylonian volume meassurement: 1 gin
        Metrology:  gan <-100- sar <-60- gin <-180- se
        Factor with unit 'se':  1 180 10800 1080000
    Meassurement in terms of the smallest unit: 180 (se)
    Sexagesimal floating value of the above: 3
    Approximate SI value: 0.3 cube meters
    --> 

#### Bricks

Volume measurements were frequently transformed into their "brick" equivalents. These were measured in "*sar-b*" (units or packages of 720 bricks), and each brick type was characterized by its "*Nalbanum*," or the number of *sar-b* of that type that fits in 1 *sar* of volume. The `.sarb()` method allows us to perform this transformation:

    --> a = bv('1 sar')
    --> a
    1 sar
    --> b = a.bricks()
    --> b
    1 sar
    --> b.explain()
    This is a Babylonian brick counting: 1 sar
        Metrology:  gan <-100- sar <-60- gin <-180- se
        Factor with unit 'se':  1 180 10800 1080000
    Meassurement in terms of the smallest unit: 10800 (se)
    Sexagesimal floating value of the above: 3
    Approximate SI value: 720.0 bricks

This is for  *nalbanum* =1.0  type-12 bricks, for type-2 bricks with decimal *nalbanum* = 7.20:

    --> b = a.bricks(7.20)
    --> b
    7 sar 12 gin
    --> b.SI()
    '5184.0 bricks'
    --> 

If you have 10000 type-2 bricks, you can do:

    --> c = bb(15 * 10000)
    --> c
    13 sar 53 gin 60 se
    --> c.SI()
    '10000.0 bricks'

`c` is a Bbri object:

    --> c.explain()
    This is a Babylonian brick counting: 13 sar 53 gin 60 se
        Metrology:  gan <-100- sar <-60- gin <-180- se
        Factor with unit 'se':  1 180 10800 1080000
    Meassurement in terms of the smallest unit: 150000 (se)
    Sexagesimal floating value of the above: 41:40
    Approximate SI value: 10000.0 bricks
    --> 

that you can convert into a volume:

    --> d = c.vol(7.20)
    --> d.explain()
    This is a Babylonian volume meassurement: 1 sar 55 gin 133 se
        Metrology:  gan <-100- sar <-60- gin <-180- se
        Factor with unit 'se':  1 180 10800 1080000
    Meassurement in terms of the smallest unit: 20833 (se)
    Sexagesimal floating value of the above: 5:47:13
    Approximate SI value: 34.721666666666664 cube meters
    >>>

Here is an excerpt from a table found
[here](https://personal.us.es/cmaza/mesopotamia/edificios.htm#Tipos%20de%20ladrillos) (Spanish only, sorry):

|Brick type|Nalb. (dec.) |Nalb. (sex.)|
|------|---------|-----|
|  1   |    9.00 |9|
|  1a  |     8.33| 8:20|
|  2   |     7.20 |7:12|
|3 |  5.40 | 5:24|
|4 |   5.00 |5|
|5 |  4.80 |4:48|
|7 |   3.33 |3:20|
|8 |  2.70 |2:42|
|9 |  2.25 |2:15|
|10|  1.875 |1:52:30|
|11|  1.20| 1:12|
|12|1.00 |1  |



