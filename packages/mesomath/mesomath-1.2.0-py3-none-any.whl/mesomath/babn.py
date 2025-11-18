"""This module implements class Babn for sexagesimal representation of the natural numbers
and their basic arithmetic operations, especially in their "floating" version,
as performed by Babylonian scribes. Hence the name."""

from math import log, sqrt
from os.path import exists
from sqlite3 import connect
from types import NotImplementedType
from typing import Final, Self


class BabN:
    """This class implements a sexagesimal representation of the natural numbers
    and their basic arithmetic operations, especially in their "floating" version,
    as performed by Babylonian scribes. Hence the name.

    Class attributes:
    -----------------

    :title: Describe the type of object
    :type title: str
    :sep: separator for string representation (default: ":")
    :type sep: str, (default: ":")
    :fill: if True writes: "01.33.07" instead of "1.33.7"
    :type fill: bool,  (default: False)
    :rdigits: approximate number of sexagesimal digits for some results
    :type rdigits: int, (default: 6:)
    :floatmult: If True, multiplication result is floating
    :type floatmult: bool, (default: False)
    :database: path to SQLite3 database of regular numbers providing:

        | regular:    TEXT, regular number e.g. 01:18:43:55:12
        | len:     INTEGER, its length e.g. 5 for 01:18:43:55:12
        | see ``createDB.py`` or ``hamming.py`` for how to generate it

    :type database: str, (default: "regular.db3")

    Instance attributes:
    --------------------

    :dec: decimal versión of number (ex: 405 for sexagesimal "6:45")
    :type dec: int
    :list: list of sexagesimal digits of number (ex: [6, 45] for 405 or "6:45")
    :type list: list
    :isreg: True if number is regular (only contains 2, 3, 5 as divisors)
    :type isreg: bool
    :factors: tuple with the powers of 2, 3, 5 and the remainder
    :type factors: tuple

    jccsvq fecit, 2005. Public domain.

    Operators
    ---------

    This class overloads arithmetic and logical operators allowing arithmetic
    operations and comparisons to be performed between members of the class and
    externally with integers. Comparing with any other object type will raise
    ``NotImplementedError``.

    """

    title: str = "Sexagesimal number"
    sep: str = ":"
    fill: bool = False
    rdigits: int = 6
    floatmult: bool = False
    database: str = "regular.db3"

    @staticmethod
    def dec2list(n: int) -> list:
        """
        Convert decimal integer n to list of int's (its sexagesimal digits)

        :n: Decimal integer to be converted
        :ntype: int

        """
        if n < 60:
            return [n]
        else:
            rlist = []
            while n >= 60:
                rlist.append(n % 60)
                n = n // 60
            if n > 0:
                rlist.append(n)
            rlist.reverse()
        return rlist

    @staticmethod
    def parse(n: int | str | list | tuple) -> tuple | None:
        """Returns tuple with decimal value and list of sexagesimal digits of n.

        :n: may be

            | an integer (sign is ignored),
            | a correctly formated string (e.g., 405, "02:45" or "2.45"),
            | a list (e.g., [1, 12, 23])
            | a tuple (e.g., (i,j,k,l) such that  2**i * 3**j * 5**k * l is the
            |   decimal value of the number

        """
        if type(n) is list:
            lt = n
            rs = 0
            for i in lt:
                rs = rs * 60 + i
            return (rs, BabN.dec2list(rs))
        elif type(n) is int:
            return (abs(n), BabN.dec2list(abs(n)))
        elif type(n) is str:
            if n.find(":") > 0:
                lt = [int(j) for j in n.split(":")]
            elif n.find(".") > 0:
                lt = [int(j) for j in n.split(".")]
            else:
                lt = [int(n)]
            rs = 0
            for i in lt:
                rs = rs * 60 + i
            return (rs, BabN.dec2list(rs))
        elif type(n) is tuple:
            i, j, k, ll = n
            rs = 2**i * 3**j * 5**k * ll
            return (rs, BabN.dec2list(rs))
        else:
            print("Invalid argument!")
            return None

    @staticmethod
    def genDB(dbname: str) -> None:
        """Generates sqlite3 database of regular numbers

        :dbname: database path and name
        :type dbname: str

        """
        sqlhead = """
        CREATE TABLE regulars (
        id INTEGER PRIMARY KEY,
        regular    TEXT,
        len     INTEGER
        );
        """
        from mesomath.hamming import hamming

        sqltail = """CREATE UNIQUE INDEX regs ON regulars (regular);
        """

        rlist = hamming(1, 79405)
        i = 0
        BabN.fill = True

        con = connect(dbname)
        cur = con.cursor()
        cur.execute("DROP TABLE IF EXISTS regulars;")
        cur.execute(sqlhead)

        for x in rlist:
            if x % 60 != 0:
                i += 1
                n = BabN(x)
                nlen = n.len()
                cur.execute(f"INSERT INTO regulars VALUES({i},'{n}',{nlen});")
        cur.execute(sqltail)
        con.commit()
        con.close()
        print(f"""...(Database: {dbname} created!)...""")

    @classmethod
    def create_new(cls, data) -> Self:
        """
        Class method that returns a new instance.
        """
        return cls(data)

    def __init__(self, n: int | str | list | tuple) -> None:
        """
        Class constructor

        :n: The parameter n can be an integer (sign is ignored) or a properly
            formatted string representing a sexagesimal number, accepting the
            separators ":" and "." (e.g., 405, "02:45" or "2.45") or a list
            (e.g., [1, 12, 23]) or a tuple (e.g., (i,j,k,l) such that
            2**i * 3**j * 5**k * l is the decimal value of the number.

        """
        tup = BabN.parse(n)
        if tup is None:
            return None
        (dec, ll) = tup
        if dec == 1:
            isreg = True
            ll = [1]
            factors = (0, 0, 0, 1)
        elif dec == 0:
            isreg = False
            ll = [0]
            factors = (0, 0, 0, 0)
        else:
            x = dec
            i = j = k = 0
            while x % 2 == 0:
                i += 1
                x //= 2
            while x % 3 == 0:
                j += 1
                x //= 3
            while x % 5 == 0:
                k += 1
                x //= 5
            if x > 1:
                isreg = False
            else:
                isreg = True
            factors = (i, j, k, x)

        self.__dec: Final[int] = dec
        self.__list: Final[list[int]] = ll
        self.__factors: Final[tuple[int, int, int, int]] = factors
        self.__isreg: Final[bool] = isreg

    @property
    def dec(self):
        """Getter"""
        return self.__dec

    @property
    def list(self):
        """Getter"""
        return self.__list

    @property
    def factors(self):
        """Getter"""
        return self.__factors

    @property
    def isreg(self):
        """Getter"""
        return self.__isreg

    def inv(self, digits: int = 4) -> Self | None:
        """Returns BabN object with approximate inverse of the number,
        i.e., a * a.inv() is approximately a power of 60

        :digits: the intended number of digits to return.
        :type digits: int, default 4.

        """
        x = self.dec
        if x == 0:
            print("This number has no inverse!")
            return None
        nsd = int(log(x) / log(60))
        inv = (pow(60, nsd + digits)) / x
        inv = int(round(inv, 0))
        while inv % 60 == 0:
            inv //= 60
        return self.create_new(inv)

    def f(self) -> Self:
        """Returns BabN object with the floating part of the number (mantissa),
        i.e., removes any trailing sexagesimal zero, ex.: 4:42:0:0 -> 4:42"""
        ll = self.list
        if self.dec == 0:
            return self
        while ll[-1] == 0:
            ll = ll[:-1]
        return self.create_new(ll)

    float = f

    def len(self) -> int:
        """Returns the number of sexagesimal digits of the number as int"""
        return len(self.list)

    def head(self, d: int = 1) -> Self:
        """Returns BabN object with the first d digits of self

        :d: Number of digits to return

        """
        lm = min(abs(d), len(self.list))
        return self.create_new(self.list[:lm])

    def tail(self, d: int = 1) -> Self:
        """Returns BabN object with the last d digits of self

        :d: Number of digits to return

        """
        ll = min(abs(d), len(self.list))
        return self.create_new(self.list[-ll:])

    def trim(self, d: int) -> Self:
        """Returns BabN object corresponding to the first d sexagesimal digits

        :d: Number of digits to retain

        """
        if d <= self.len():
            return self.create_new(self.list[:d])
        else:
            return self

    def round(self, d: int) -> Self:
        """Returns BabN object rounded to d sexagesimal digits

        :d: Number of digits to return

        """
        if d < self.len():
            ll = self.list
            if ll[d] >= 30:
                return self.create_new(ll[:d]) + self.create_new(1)
            else:
                return self.create_new(ll[:d])
        else:
            return self

    def __add__(self, other) -> Self | NotImplementedType:
        """Overloads `+` operator: returns BabN object with the sum of operands

        :other: May be another BabN object or a positive int.

        """
        if isinstance(other, BabN):
            return self.create_new(self.dec + other.dec)
        elif isinstance(other, int):
            return self.create_new(self.dec + abs(other))
        else:
            return NotImplemented

    def __radd__(self, other: int) -> Self | NotImplementedType:
        """Overloads `+` operator: returns BabN object with the sum of operands

        :other: a positive int.

        """
        if isinstance(other, int):
            return self.create_new(self.dec + abs(other))
        else:
            return NotImplemented

    def __sub__(self, other) -> Self | NotImplementedType:
        """Overloads `-` operator: returns BabN object with the absolute value
        of the operands difference

        :other: May be another BabN object or a positive int.

        """
        if isinstance(other, BabN):
            return self.create_new(abs(self.dec - other.dec))
        elif isinstance(other, int):
            return self.create_new(abs(self.dec - abs(other)))
        else:
            return NotImplemented

    def __rsub__(self, other) -> Self | NotImplementedType:
        """Overloads `-` operator: returns BabN object with the absolute value
        of the operands difference

        :other: May be another BabN object or a positive int.

        """
        if isinstance(other, int):
            return self.create_new(abs(self.dec - abs(other)))
        else:
            return NotImplemented

    def __mul__(self, other) -> Self | NotImplementedType:
        """Overloads `*` operator: returns BabN object with the operands product

        :other: May be another BabN object or a positive int.

        """
        if isinstance(other, BabN):
            if BabN.floatmult:
                return self.create_new(self.dec * other.dec).float()
            else:
                return self.create_new(self.dec * other.dec)
        elif isinstance(other, int):
            if BabN.floatmult:
                return self.create_new(self.dec * other).float()
            else:
                return self.create_new(self.dec * other)
        else:
            return NotImplemented

    def __rmul__(self, other) -> Self:
        """Overloads `-` operator: returns BabN object with the operands product

        :other: May be another BabN object or a positive int.

        """
        if BabN.floatmult:
            return self.create_new(self.dec * other).float()
        else:
            return self.create_new(self.dec * other)

    def __truediv__(self, other) -> Self | None:
        """Overloads `/` operator:  Returns BabN object with the floating
        approximate division of operands

        :other: May be another BabN object or a positive int.

        """
        a = self.dec
        if isinstance(other, BabN):
            b = other.dec
        elif isinstance(other, int):
            b = other
        try:
            q = a / b
        except ZeroDivisionError:
            print("Oops!  Cannot divide by zero")
            return None
        nsd = int(log(q) / log(60))
        inv = pow(60, BabN.rdigits - nsd) * q
        inv = int(round(inv, 0))
        while inv % 60 == 0:
            inv //= 60
        return self.create_new(inv)

    def __rtruediv__(self, other) -> Self | None:
        """Overloads `/` operator:  Returns BabN object with the floating
        approximate division of operands

        :other: May be another BabN object or a positive int.

        """
        # return (self.create_new(other)).__truediv__(self)
        return (self.create_new(other)) / (self)
        # return other.__truediv__(self)

    def __floordiv__(self, other) -> Self | None:
        """Overloads `//` operator: Returns BabN object with the result of
        "Babylonian división" of operands, i.e., if b is regular then a//b
        returns a times the reciprocal of b. Result is floating. Returns None
        if b is not regular.

        :other: May be another BabN object or a positive int.

        """
        if isinstance(other, int):
            other = BabN(other)
        if other.isreg:
            inv = other.rec().dec
            q = self.dec * inv
            while q % 60 == 0:
                q //= 60
            return self.create_new(q)
        else:
            print("Divisor is not a regular number (igi nu)!")
            return None

    def __rfloordiv__(self, other) -> Self | None:
        """Overloads `//` operator: Returns BabN object with the result of
        "Babylonian división" of operands, i.e., if b is regular then a//b
        returns a times the reciprocal of b. Returns None if b is not regular.

        :other: May be another BabN object or a positive int.

        """
        # return self.create_new(other).__floordiv__(self)
        return (self.create_new(other)) // (self)

    def __pow__(self, x: int) -> Self | None:
        """Overloads `**` operator: Returns BabN object with the number raised
        to the power x where x is a natural integer

        :x: power, positive int.

        """
        try:
            return self.create_new(self.dec**x)
        except Exception:
            print("x must be a positive integer")
            return None

    def __lt__(self, other)-> bool:
        """Overloads < operator

        :other: May be another BabN object or a positive int.

        """
        if isinstance(other, BabN):
            return self.dec < other.dec
        elif isinstance(other, int):
            return self.dec < other
        else:
            raise NotImplementedError

    def __le__(self, other)-> bool:
        """Overloads <= operator

        :other: May be another BabN object or a positive int.
        :raises: ``NotImplementedError`` if ``other`` is any other object.

        """
        if isinstance(other, BabN):
            return self.dec <= other.dec
        elif isinstance(other, int):
            return self.dec <= other
        else:
            raise NotImplementedError

    def __eq__(self, other) -> bool:
        """Overloads == operator

        :other: May be another BabN object or a positive int.
        :raises: ``NotImplementedError`` if ``other`` is any other object.

        """
        if isinstance(other, BabN):
            return self.dec == other.dec
        elif isinstance(other, int):
            return self.dec == other
        else:
            raise NotImplementedError

    def __ne__(self, other) -> bool:
        """Overloads != operator

        :other: May be another BabN object or a positive int.
        :raises: ``NotImplementedError`` if ``other`` is any other object.

        """
        if isinstance(other, BabN):
            return self.dec != other.dec
        elif isinstance(other, int):
            return self.dec != other
        else:
            raise NotImplementedError

    def __gt__(self, other) -> bool:
        """Overloads > operator

        :other: May be another BabN object or a positive int.
        :raises: ``NotImplementedError`` if ``other`` is any other object.

        """
        if isinstance(other, BabN):
            return self.dec > other.dec
        elif isinstance(other, int):
            return self.dec > other
        else:
            raise NotImplementedError

    def __ge__(self, other) -> bool:
        """Overloads >= operator

        :other: May be another BabN object or a positive int.
        :raises: ``NotImplementedError`` if ``other`` is any other object.

        """
        if isinstance(other, BabN):
            return self.dec >= other.dec
        elif isinstance(other, int):
            return self.dec >= other
        else:
            raise NotImplementedError

    def rec(self) -> Self:
        """Returns BabN object with the reciprocal of a regular number, returns
        None for non-regular numbers"""
        if self.isreg:
            x = self.dec
            while x % 60 == 0:
                x //= 60
            if x == 1:
                return self.create_new(1)
            i = j = k = 0
            while x % 2 == 0:
                i += 1
                x //= 2
            while x % 3 == 0:
                j += 1
                x //= 3
            while x % 5 == 0:
                k += 1
                x //= 5

            i0 = j0 = k0 = 0
            if i % 2 == 1:
                i0 += 1
                i += 1
            if j > k:
                k0 += j - k
                k += j - k
            if k > j:
                j0 += k - j
                j += k - j
            if i < 2 * j:
                i0 += 2 * j - i
                i += 2 * j - i
            if i > 2 * j:
                t = (i - 2 * j) // 2
                j += t
                k += t
                j0 += t
                k0 += t
            return self.create_new(pow(2, i0) * pow(3, j0) * pow(5, k0))
        else:
            print("Not regular, (igi nu)!")
            return None

    def sqrt(self) -> Self:
        """Returns BabN object with approximate floating square root"""
        digits = BabN.rdigits - 1
        x = self.dec
        sqr = (pow(60, digits)) * sqrt(x)
        sqr = int(round(sqr, 0))
        while sqr % 60 == 0:
            sqr //= 60
        return self.create_new(sqr)

    def cbrt(self) -> Self:
        """Returns BabN object with approximate floating cube root"""
        digits = BabN.rdigits - 1
        x = self.dec
        cbr = (pow(60, digits)) * x ** (1.0 / 3)
        cbr = int(round(cbr, 0))
        while cbr % 60 == 0:
            cbr //= 60
        return self.create_new(cbr)

    def dist(self, n: str | int | type(Self)) -> int:
        """Estimates a certain "distance" between two sexagesimal numbers.

        The objective is, given a non-regular number, to select the regular
        number that is closest to it from a list.

        :n: may be an integer, formated string (ex: "1:2:3"), a list (ex., [1, 12, 23]) or another BabN object. Returns int.

        """
        list1 = [] + self.list
        len1 = self.len()
        if type(n) is BabN:
            list2 = [] + n.list
            len2 = n.len()
            print(self.dec, n.dec)
        else:
            (ndec, list2) = __class__.parse(n)
            len2 = len(list2)
        if len1 > len2:
            list2 += [0 for i in range(len1 - len2)]
        elif len2 > len1:
            nextd = list2[len1]
            list2 = list2[:len1]
            if nextd > 30:
                list2[-1] += 1
        return (BabN(list1) - BabN(list2)).dec

    def searchreg(
        self,
        minn: str | int,
        maxn: str | int,
        limdigits: int = 6,
        prt: bool = False,
    ) -> Self:
        """Search database for regulars between sexagesimals minn y maxn.
        Returns BabN object with the closest regular found.

        :minn and maxn: must be sexagesimal strings using ":" separator
        :limdigits: max regular digits number (default: 6)
        :prt: print list of found regulars (default: False)

        Returns the closest regular as a BabN object
        """

        if not exists(BabN.database):
            __class__.genDB(BabN.database)

        conn = connect(BabN.database)
        cursor = conn.cursor()
        sql_line = """
SELECT regular
  FROM regulars
 WHERE len <= ? AND 
       regular BETWEEN ? AND ?
 ORDER BY regular
;
"""
        cursor.execute(sql_line, (limdigits, minn, maxn))
        rl = cursor.fetchall()
        conn.commit()
        conn.close()

        tmplist = [] + self.list
        if len(tmplist) < limdigits:
            tmplist = tmplist + [0 for i in range(limdigits - len(tmplist))]

        a = BabN(tmplist)
        mind = a.dist(rl[0][0])
        minr = rl[0][0]
        for i in rl:
            if prt:
                print(f" {a.dist(i[0]):12d} {i[0]}")
            ndis = a.dist(i[0])
            if ndis < mind:
                mind = ndis
                minr = i[0]
        if prt:
            print(f"Minimal distance: {mind}, closest regular is: {minr}")
        return self.create_new(minr)

    def explain(self) -> None:
        """Explains number; print out basic information about the object."""
        print(f"|  Sexagesimal number: {self.list} is the decimal number: {self.dec}.")
        (i, j, k, x) = self.factors
        print(f"|    It may be written as (2^{i} * 3^{j} * 5^{k} * {x}),")
        if self.isreg:
            print(f"|    so, it is a regular number with reciprocal: {self.rec()}")
        else:
            print("|    so, it is NOT a regular number and has NO reciprocal.")
            print(f"|    but an approximate inverse is: {self.inv()}")
            cr = self.searchreg("01:0", "59:59", 5, 0)
            if cr is not None:
                print(f"|    and a close regular is: {cr}")
                print(f"|    whose reciprocal is: {cr.rec()}")

    def __repr__(self) -> str:
        """Returns string representation of sexagesimal number."""
        rlist = self.list
        if self.fill:
            tt = list(map(str, rlist))
            for i in range(len(tt)):
                if len(tt[i]) == 1:
                    tt[i] = "0" + tt[i]
            return BabN.sep.join(tt)
        else:
            return BabN.sep.join(map(str, rlist))

    def __hash__(self) -> int:
        """Returns hash value of the instance"""
        return hash((type(self), self.__dec))

    def __int__(self) -> int:
        """Converts instance to int"""
        return self.__dec

    __len__ = len
    __round__ = round
