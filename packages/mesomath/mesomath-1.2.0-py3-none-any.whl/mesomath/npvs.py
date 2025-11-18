"""This module implements classes for Non-Place-Value numeration system and
related arithmetic. Intended for Mesopotamian metrological systems,
but class Npvs is of general use.

* class  Npvs: Generic class inspired in Imperial Units System lengths

    * class _MesoM: Specializes the Npvs class to handle Mesopotamian counting.

        * class  BsyG: Babylonian System G
        * class  BsyS: Babylonian System S
        * class MesoM: Specializes the Npvs class to handle Mesopotamian measurements.

            * class  Blen: Babylonian length system
            * class  Bsur: Babylonian surface system
            * class  Bvol: Babylonian volume system
            * class  Bcap: Babylonian capacity system
            * class  Bwei: Babylonian weight system
            * class  Bbri: Babylonian brick counting system

"""

from re import sub
from typing import Final, Self
from mesomath.babn import BabN

# Data
#: Dictionary of principal fractions withouth 1/6
fdic0: Final[dict] = {
    3: (["2/3", "1/3"], [2, 1]),
    5: ([""], []),
    10: (["1/2"], [5]),
    6: (["5/6", "2/3", "1/2", "1/3"], [5, 4, 3, 2]),
    12: (["5/6", "2/3", "1/2", "1/3"], [10, 8, 6, 4]),
    30: (["5/6", "2/3", "1/2", "1/3"], [25, 20, 15, 10]),
    60: (["5/6", "2/3", "1/2", "1/3"], [50, 40, 30, 20]),
    100: (["1/2"], [50]),
    180: (["5/6", "2/3", "1/2", "1/3"], [150, 120, 90, 60]),
}

#: Dictionary of principal fractions including 1/6
fdic1: Final[dict] = {
    3: (["2/3", "1/3"], [2, 1]),
    5: ([""], []),
    10: (["1/2"], [5]),
    6: (["5/6", "2/3", "1/2", "1/3", "1/6"], [5, 4, 3, 2, 1]),
    12: (["5/6", "2/3", "1/2", "1/3", "1/6"], [10, 8, 6, 4, 2]),
    30: (["5/6", "2/3", "1/2", "1/3", "1/6"], [25, 20, 15, 10, 5]),
    60: (["5/6", "2/3", "1/2", "1/3", "1/6"], [50, 40, 30, 20, 10]),
    100: (["1/2"], [50]),
    180: (["5/6", "2/3", "1/2", "1/3", "1/6"], [150, 120, 90, 60, 30]),
}


# Functions
def cmul(x: list[int]) -> list[int]:
    """Utility function. Returns list of cumulative products of the factor list x

    :x: list of ints
    :raises: TypeError

    Example: cmul([4,3,3,22,10,8,3]) returns:
         [1, 4, 12, 36, 792, 7920, 63360, 190080]"""
    if isinstance(x, list):
        prod = 1
        prodl = [1]
        for i in x:
            prod *= i
            prodl.append(prod)
        return prodl
    else:
        raise TypeError


def normalize(st: str) -> str:
    """Converts aname's to unit names and standardizes fractions.

    :st: input strig to be normalized

    """

    # Consolidate character and word replacements
    replacements = {
        r"[šŠ]": "s",
        r"([a-zA-Z])(['23\-]+)": r"\g<1>",
        r"GAN": "gan",
        r"U": "u",
    }

    # Pre-compile patterns for efficiency
    for pattern, repl in replacements.items():
        st = sub(pattern, repl, st)

    # Normalizing fractions
    st = sub(r"1/6|1/3|1/2|2/3|5/6", r"+\g<0>", st)
    st = sub(r" *\+ *", "+", st)
    st = sub(r"[a-z]\+", r"\g<0>+", st)
    st = sub(r" *\++", "+", st)
    st = sub(r"([a-z])(\+)", r"\g<1> 0+", st)

    # Clean up spacing
    st = sub(r"\s+", " ", st).strip()

    # Handle leading fractions
    if st.startswith("+"):
        st = "0" + st

    return st


# Classes
class Npvs:
    """This class implement Non-Place-Value System arithmetic
           Example is taken from Imperial length units:

           **league <-3- mile <-8- furlong <-10- chain <-22- yard <-3- foot
           <-3- hand <-4- inch**

    Class Atributes:
    ----------------

    :title: Definition of the object
    :uname: Unit names
    :ufact: Factor between units
    :aname: Actual or academic unit names
    :cfact: Factor with the smallest unit
    :siv: S.I. value of the smallest unit
    :siu: S.I. unit name
    :prtsex: Printing meassurements in sexagesimal (default: False)


    Instance Attributes:
    --------------------

    :dec: Decimal value of meassurement in terms of the smallest unit
    :list: List of values per unit

    Operators
    ---------

    This class overloads arithmetic and logical operators allowing arithmetic
    operations and comparisons to be performed between members of the class.
    Comparison with other objects raises ``NotImplementedError``.

    jccsvq fecit, 2005. Public domain.

    """

    title: str = "Imperial length meassurement"
    uname: list[str] = "in hh ft yd ch fur mi lea".split()  # Unit names
    aname: list[str] = (
        "inch hand foot yard chain furlong mile league".split()
    )  # Actual unit names
    ufact: list[int] = [4, 3, 3, 22, 10, 8, 3]  # Factor between units
    cfact: list[int] = [
        1,
        4,
        12,
        36,
        792,
        7920,
        63360,
        190080,
    ]  # Factor with the smallest unit
    siv: float = 0.0254  # meters per inch
    siu: str = "meters"  # S.I. unit name

    def scheme(self, actual: bool = False) -> list:
        """Returns list with the unit names separated by the corresponding factors

        :actual: Uses actual or academic unit names if True (default: False)

        Example:

            >>> print(*Npvs.scheme(Npvs))
            lea <-3- mi <-8- fur <-10- ch <-22- yd <-3- ft <-3- hh <-4- in

            >>> print(*Npvs.scheme(Npvs,actual=1))
            league <-3- mile <-8- furlong <-10- chain <-22- yard <-3- foot <-3- hand <-4- inch

        """
        ll = []
        if actual:
            for i in range(len(self.ufact)):
                ll.append(self.aname[i])
                ll.append("<-" + str(self.ufact[i]) + "-")
            ll.append(self.aname[-1])
        else:
            for i in range(len(self.ufact)):
                ll.append(self.uname[i])
                ll.append("<-" + str(self.ufact[i]) + "-")
            ll.append(self.uname[-1])
        ll.reverse()
        return ll

    def dec2un(self, x: int) -> list:
        """
        Converts the decimal integer n to a list of integers, such that, for
        example, 1001 (inches) becomes ``[1, 1, 2, 5, 1, 0, 0, 0]``, which means
        that 1001 inches equals: 1 chain 5 yards 2 feet 1 hand 1 inch.

        """
        result = []
        for i in self.ufact:
            result.append(x % i)
            x //= i
        result.append(x)
        return result

    def sexsys(self, x):
        return NotImplemented

    def __init__(self, x: int | str) -> None:
        """Class constructor

        :n: The parameter n can be an integer (sign is ignored) or a properly
         formatted string representing the value. See the tutorial

        """
        if type(x) is int:
            x = abs(x)
            dec = x
            lista = self.dec2un(x)
        elif type(x) is str:
            if x.find("(") >= 0:
                xx = x.split("(")[1:]
                xnew = ""
                for i in xx:
                    xy = i.split(")")
                    coef = self.sexsys(xy[0])
                    xnew += str(coef.dec) + " "
                    xnew += xy[1] + " "
                #                print(xnew)
                x = xnew
            ll = x.split()
            l1 = ll[::2]
            l2 = ll[1::2]
            t = 0
            for _ in range(len(l2)):
                j = self.uname.index(l2[_])
                t += int(l1[_]) * self.cfact[j]
            dec = t
            lista = self.dec2un(t)
        self.__dec: Final[int] = dec
        self.__list: Final[list[int]] = lista

    @property
    def dec(self):
        """Getter"""
        return self.__dec

    @property
    def list(self):
        """Getter"""
        return self.__list

    def __add__(self, other: Self) -> Self | None:
        """Overloads ``+`` operator: returns object with the sum of operands

        :other: another Npvs object or instance

        """
        if type(other) is type(self):
            return self.__class__(self.dec + other.dec)
        else:
            return None

    def __sub__(self, other: Self) -> Self | None:
        """Overloads ``+`` operator: returns object with the absolute difference
        of operands

        :other: another Npvs object or instance

        """
        if type(other) is type(self):
            return self.__class__(abs(self.dec - other.dec))
        else:
            return None

    def __mul__(self, other: int | float) -> Self:
        """Overloads ``*`` operator: returns object with the operands product

        :other: a positive int or float

        """
        t = self.dec * other
        return self.__class__(int(round(t, 0)))

    def __rmul__(self, other) -> Self:
        """Overloads ``*`` operator: returns object with the operands product

        :other: a positive int or float

        """
        return self.__mul__(other)

    def __truediv__(self, other: int | float) -> Self:
        """Overloads ``/`` operator: returns object with the operands product

        :other: a positive int or float

        """
        return self.__class__(int(round(self.dec / other, 0)))

    def si(self) -> float:
        """Returns the numeric equivalent in SI units"""
        return self.dec * self.siv

    def SI(self) -> str:
        """Returns formated string with the equivalent in SI units"""
        return f"{self.dec * self.siv} {self.siu}"

    def __lt__(self, other: Self) -> bool:
        """Overloads ``<`` operator

        :other: another Npvs object

        """
        if isinstance(other, type(self)):
            return self.dec <= other.dec
        else:
            raise NotImplementedError

    def __le__(self, other: Self) -> bool:
        """Overloads ``<=`` operator

        :other: another Npvs object

        """
        if isinstance(other, type(self)):
            return self.dec <= other.dec
        else:
            raise NotImplementedError

    def __eq__(self, other: object) -> bool:
        """Overloads ``==`` operator

        :other: another Npvs object

        """
        if isinstance(other, type(self)):
            return self.dec == other.dec
        else:
            raise NotImplementedError

    def __ne__(self, other: object) -> bool:
        """Overloads ``!=`` operator

        :other: another Npvs object

        """
        if isinstance(other, type(self)):
            return self.dec != other.dec
        else:
            raise NotImplementedError

    def __gt__(self, other: Self) -> bool:
        """Overloads ``>`` operator

        :other: another Npvs object

        """
        if isinstance(other, type(self)):
            return self.dec > other.dec
        else:
            raise NotImplementedError

    def __ge__(self, other: Self) -> bool:
        """Overloads ``>=`` operator

        :other: another Npvs object

        """
        if isinstance(other, type(self)):
            return self.dec >= other.dec
        else:
            raise NotImplementedError

    def __repr__(self) -> str:
        """Returns string representation of object"""
        ss = []
        for i in reversed(range(len(self.uname))):
            if self.list[i] != 0:
                ss.append(str(self.list[i]))
                ss.append(self.uname[i])
        return " ".join(ss)

    def __hash__(self):
        """Returns hash value of the instance"""
        return hash((type(self), self.dec))

    def __int__(self):
        """Converts instance to int"""
        return self.dec


class _MesoM(Npvs):
    """
    Specializes the Npvs class to handle Mesopotamian measurements.

    Introduces the .sex(), .metval() and .explain() methods and the .prtsex attribute.
    Modifies __repr__()

    :meta public:
    """

    title: str = "Sexagesimal sistem"
    uname: list[str] = "sa sb sc sd".split()  # Unit names
    aname: list[str] = "Ša Šb Šc Šd".split()  # Unit names
    ufact: list[int] = [60, 60, 60]  # Factor between units
    cfact: list[int] = [1, 60, 3600, 216000]  # Factor with the smallest unit
    siv: float = 1.0  #
    siu: str = "counts"  # S.I. unit name
    prtsex: bool = False  # Printing meassurements in sexagesimal
    ubase: int = 0  # Base unit for metrological tables

    def __init__(self, x: int | str) -> None:
        """Class constructor

        | n: The parameter n can be an integer (sign is ignored) or a properly
             formatted string representing the value. See the tutorial"""
        if type(x) is int:
            x = abs(x)
            dec = x
            lista = self.dec2un(x)
        elif type(x) is str:
            x = normalize(x)
            if x.find("(") >= 0:
                xx = x.split("(")[1:]
                xnew = ""
                for i in xx:
                    xy = i.split(")")
                    if xy[-1].find(self.uname[-1]) >= 0:
                        coef = self.sexsys(xy[0])
                    else:
                        coef = self.sexsys(xy[0])
                    xnew += str(coef.dec) + " "
                    xnew += xy[1] + " "
                xnew = sub(r" *\+", "+", xnew)
                #                print(xnew)
                x = xnew
            ll = x.split()
            l1 = ll[::2]
            l2 = ll[1::2]
            t = 0
            for _ in range(len(l2)):
                j = self.uname.index(l2[_])
                if l1[_].find("+") >= 0:
                    l3 = l1[_].split("+")
                    t += int(l3[0]) * self.cfact[j]
                    if l3[1] == "1/6":
                        t += self.cfact[j] // 6
                    elif l3[1] == "1/3":
                        t += self.cfact[j] // 3
                    elif l3[1] == "1/2":
                        t += self.cfact[j] // 2
                    elif l3[1] == "2/3":
                        t += 2 * self.cfact[j] // 3
                    elif l3[1] == "5/6":
                        t += 5 * self.cfact[j] // 6
                else:
                    t += int(l1[_]) * self.cfact[j]
            dec = t
            lista = self.dec2un(t)
        self.__dec: Final[int] = dec
        self.__list: Final[list[int]] = lista

    @property
    def dec(self):
        """Getter"""
        return self.__dec

    @property
    def list(self):
        """Getter"""
        return self.__list

    def sex(self, r: int = 0) -> BabN | None:
        """Return sexagesimal floating value of object

        :r: index of reference unit in uname

        """

        return BabN(self.dec) // self.cfact[r]

    def metval(self) -> BabN | None:
        """Returns metrological value of object"""
        return self.sex(r=self.ubase)

    def explain(self) -> None:
        """Print some information about the object"""
        print(f"This is a {self.title}: {self}")
        print("    Metrology: ", *self.scheme())
        print(f"    Factor with unit '{self.uname[0]}': ", *self.cfact)
        print(
            f"Meassurement in terms of the smallest unit: {self.dec} ({self.uname[0]})"
        )
        print(f"Sexagesimal floating value of the above: {self.sex(False)}")
        print(f"Approximate SI value: {self.SI()}")

    def prtf(self, onesixth: bool = False, actual: bool = False) -> str:
        """Alternative to __repr__() to use the fractions 1/3, 1/2, 2/3, 5/6 of
        the units in the output

        :onesixth: Adds 1/6 to the previous set of fractions if True
        :type onesixth: bool, (default = False)
        :actual: if True, uses academic unit names on output
        :type actual: bool, (default: False)

        """
        if onesixth:
            fdic = fdic1
        else:
            fdic = fdic0
        length = len(self.list)
        ll = self.list.copy()
        ff = ["" for i in range(length)]
        for i in range(length - 1):
            k = self.ufact[i]
            (zfrac, z) = fdic[k]
            for j in range(len(z)):
                if ll[i] >= z[j]:
                    ll[i] -= z[j]
                    ff[i + 1] = zfrac[j]
                    break
        for i in range(length):
            if ll[i] == 0 and ff[i] == "":
                pass
            else:
                if ff[i] == "":
                    ff[i] = str(ll[i])
                else:
                    if ll[i] != 0:
                        ff[i] = str(ll[i]) + " " + ff[i]
        ss = ""
        for i in reversed(range(length)):
            if ff[i] != "":
                if actual:
                    ss += ff[i] + " " + self.aname[i] + " "
                else:
                    ss += ff[i] + " " + self.uname[i] + " "
        return ss[:-1]

    def __repr__(self) -> str:
        """Returns string representation of object."""
        ss = []
        for i in reversed(range(len(self.uname))):
            if self.list[i] != 0:
                if not self.prtsex:
                    ss.append(str(self.list[i]))
                    ss.append(self.uname[i])
                else:
                    if self.list[i] >= 60:
                        ss.append(
                            str(self.list[i] // 60) + ":" + str(self.list[i] % 60)
                        )
                    else:
                        ss.append(str(self.list[i]))
                    ss.append(self.uname[i])
        return " ".join(ss)


class BsyG(_MesoM):  # Babylonian System G numeration
    """This class implement Non-Place-Value System arithmetic
    for Babylonian System-G numeration

        **šar2-gal <-6- šar'u <-10- šar2 <-6- bur'u <-10- bur3 <-3- eše3 <-6- iku**

    """

    title: str = "Babylonian System G to count objects"
    uname: list[str] = "iku ese bur buru sar saru sargal".split()
    aname: list[str] = "iku eše3 bur3 bur'u šar2 šar'u šar2-gal".split()
    ufact: list[int] = [6, 3, 10, 6, 10, 6]
    cfact: list[int] = [1, 6, 18, 180, 1080, 10800, 64800]
    siv: float = 1
    siu: str = "#"
    ubase: int = 0  # iku


class BsyS(_MesoM):  # Babylonian System S numeration
    """This class implement Non-Place-Value System arithmetic
    for Babylonian System-S numeration

        **šar2-gal <-6- šar'u <-10- šar2 <-6- geš'u <-10- geš <-6- u <-10- diš**

    """

    title: str = "Babylonian System S to count objects"
    uname: list[str] = "dis u ges gesu sar saru sargal".split()
    aname: list[str] = "diš u geš geš'u šar2 šar'u šar2-gal".split()
    ufact: list[int] = [10, 6, 10, 6, 10, 6]
    cfact: list[int] = [1, 10, 60, 600, 3600, 36000, 216000]
    siv: float = 1
    siu: str = "#"
    ubase: int = 0  # dis


class MesoM(_MesoM):
    """This class complements the _MesoN class by allowing you to express unit
    coefficients in measurements using the S and G systems as appropriate. It
    introduces the sexsys attribute and enhances the __repr__ method."""

    sexsys: type[BsyS] | type[BsyG] = BsyS

    def prtf(self, onesixth: bool = False, actual: bool = False) -> str:
        """Alternative to __repr__() to use the fractions 1/3, 1/2, 2/3, 5/6 of
        the units in the output

        :onesixth: Adds 1/6 to the previous set of fractions if True
        :type onesixth: bool, (default = False)
        :actual: use academic unit names if True
        :type actual: bool, (default = False)
        """
        if onesixth:
            fdic = fdic1
        else:
            fdic = fdic0
        length = len(self.list)
        ll = self.list.copy()
        ff = ["" for i in range(length)]
        for i in range(length - 1):
            k = self.ufact[i]
            (zfrac, z) = fdic[k]
            for j in range(len(z)):
                if ll[i] >= z[j]:
                    ll[i] -= z[j]
                    ff[i + 1] = zfrac[j]
                    break
        for i in range(length):
            if ll[i] == 0 and ff[i] == "":
                pass
            else:
                if self.prtsex:
                    if ff[i] == "":
                        ff[i] = "(" + str(self.sexsys(ll[i])) + ")"
                    #                        ff[i] = '('+(self.sexsys(ll[i])).prtf(onesixth)+')'
                    else:
                        if ll[i] != 0:
                            ff[i] = "(" + str(self.sexsys(ll[i])) + ")" + " " + ff[i]
                #                            ff[i] =  '('+(self.sexsys(ll[i])).prtf(onesixth)+')'+' '+ff[i]
                else:
                    if ff[i] == "":
                        ff[i] = str(ll[i])
                    else:
                        if ll[i] != 0:
                            ff[i] = str(ll[i]) + " " + ff[i]
        ss = ""
        for i in reversed(range(length)):
            if ff[i] != "":
                if actual:
                    ss += ff[i] + " " + self.aname[i] + " "
                else:
                    ss += ff[i] + " " + self.uname[i] + " "

        return ss[:-1]

    def __repr__(self) -> str:
        """Returns string representation of object."""
        ss = []
        for i in reversed(range(len(self.uname))):
            if self.list[i] != 0:
                if not self.prtsex:
                    ss.append(str(self.list[i]))
                else:
                    if i == len(self.uname) - 1:
                        ss.append("(" + str(self.sexsys(self.list[i])) + ")")
                    else:
                        ss.append("(" + str(BsyS(self.list[i])) + ")")
                ss.append(self.uname[i])
        return " ".join(ss)


class Blen(MesoM):  # Length
    """This class implement Non-Place-Value System arithmetic
    for Old Babylonian Period length units

        **danna <-30- UŠ <-60- ninda <-12- kuš3 <-30- šu-si**

    """

    title: str = "Babylonian length meassurement"
    uname: list[str] = "susi kus ninda us danna".split()
    aname: list[str] = "šu-si kuš3 ninda UŠ danna".split()
    ufact: list[int] = [30, 12, 60, 30]
    cfact: list[int] = [1, 30, 360, 21600, 648000]
    siv: float = 0.5 / 30
    siu: str = "meters"
    ubase: int = 2  # ninda

    def __mul__(self, other):
        """Overloads ``*`` operator: returns object with the operands product

        :other: It can be a ``Blen`` or ``Bsur`` or float object and the returned product will, accordingly, be a ``Bsur`` or ``Bvol`` or ``Blen`` object.

        """
        if type(other) is Blen:
            t = int(round((self.dec * other.dec) / 12.0, 0))
            return Bsur(t)
        elif type(other) is Bsur:
            t = int(round((self.dec * other.dec) / 30.0, 0))
            return Bvol(t)
        else:
            t = self.dec * other
            return self.__class__(int(round(t, 0)))


class Bsur(MesoM):  # Surface
    """This class implement Non-Place-Value System arithmetic
    for Old Babylonian Period surface units:

        **GAN2 <-100- sar <-60- gin2 <-180- še**

    """

    title: str = "Babylonian surface meassurement"
    uname: list[str] = "se gin sar gan".split()
    aname: list[str] = "še gin2 sar GAN2".split()
    ufact: list[int] = [180, 60, 100]
    cfact: list[int] = [1, 180, 10800, 1080000]
    siv: float = 36.0 / 60 / 180
    siu: str = "square meters"
    ubase: int = 1  # gin
    sexsys: type[BsyS] | type[BsyG] = BsyG

    def __mul__(self, other):
        """Overloads ``*`` operator: returns object with the operands product

        :other: It can be a ``Blen`` or float object and the returned product will, accordingly, be a ``Bvol`` or ``Bsur`` object.

        """
        if type(other) is Blen:
            t = int(round((self.dec * other.dec) / 30.0, 0))
            return Bvol(t)
        else:
            t = self.dec * other
            return self.__class__(int(round(t, 0)))


class Bvol(MesoM):  # Volume
    """This class implement Non-Place-Value System arithmetic
    for Old Babylonian Period volume units:

        **GAN2 <-100- sar <-60- gin2 <-180- še**

    """

    title: str = "Babylonian volume meassurement"
    uname: list[str] = "se gin sar gan".split()
    aname: list[str] = "še gin2 sar GAN2".split()
    ufact: list[int] = [180, 60, 100]
    cfact: list[int] = [1, 180, 10800, 1080000]
    siv: float = 18.0 / 60 / 180
    siu: str = "cube meters"
    ubase: int = 1  # gin
    sexsys: type[BsyS] | type[BsyG] = BsyG

    def cap(self):  # noqa: F821
        """Convert volume to capacity meassurement"""
        return Bcap(18000 * self.dec)

    def bricks(self, nalb: float = 1.0):
        """Returns the volume in number of bricks equivalent based on their
        "Nalbanum." 720 for 1 sar volume if nalb is 1. Output is a ``Bbri`` object.

        :nalb: nalbanum in decimal e.g. 7.20 for type 2 bricks (defaul: 1.0)

        ==========  ============  ============
        Brick type  Nalb. (dec.)  Nalb. (sex.)
        ==========  ============  ============
        1           9.00          9
        1a          8.33          8:20
        2           7.20          7:12
        3           5.40          5:24
        4           5.00          5
        5           4.80          4:48
        7           3.33          3:20
        8           2.70          2:42
        9           2.25          2:15
        10          1.875         1:52:30
        11          1.20          1:12
        12          1.00          1
        ==========  ============  ============

        """
        tt = int(nalb * self.dec)
        return Bbri(tt)


class Bcap(MesoM):  # Capacity
    """This class implement Non-Place-Value System arithmetic
    for Old Babylonian Period capacity units:

        **gur <-5- bariga <-6- ban2 <-10- sila3 <-60- gin2 <-180- še**

    """

    title: str = "Babylonian capacity meassurement"
    uname: list[str] = "se gin sila ban bariga gur".split()
    aname: list[str] = "še gin2 sila3 ban2 bariga gur".split()
    ufact: list[int] = [180, 60, 10, 6, 5]
    cfact: list[int] = [1, 180, 10800, 108000, 648000, 3240000]
    siv: float = 1.0 / 60 / 180
    siu: str = "litres"
    ubase: int = 1  # gin

    def vol(self) -> Bvol | None:
        """Convert capacity to volume meassurement"""
        if self.dec >= 18000:
            return Bvol(self.dec // 18000)
        else:
            print("Volume too small!")
            return None


class Bwei(MesoM):  # Weight
    """This class implement Non-Place-Value System arithmetic
    for Old Babylonian Period weight units:

        **gu2 <-60- ma-na <-60- gin2 <-180- še**

    """

    title: str = "Babylonian weight meassurement"
    uname: list[str] = "se gin mana gu".split()
    aname: list[str] = "še gin2 ma-na gu2".split()
    ufact: list[int] = [180, 60, 60]
    cfact: list[int] = [1, 180, 10800, 648000]
    siv: float = 0.5 / 60 / 180
    siu: str = "kilograms"
    ubase: int = 1  # gin


class Bbri(MesoM):  # Counting bricks
    """This class implement Non-Place-Value System arithmetic
    for Old Babylonian Period counting bricks in "sar-b" units (720 bricks):

        **GAN2 <-100- sar <-60- gin2 <-180- še**

    """

    title: str = "Babylonian brick count"
    uname: list[str] = "se gin sar gan".split()
    aname: list[str] = "še gin2 sar GAN2".split()
    ufact: list[int] = [180, 60, 100]
    cfact: list[int] = [1, 180, 10800, 1080000]
    siv: float = 720.0 / 10800
    siu: str = "bricks"
    ubase: int = 1  # gin
    sexsys: type[BsyS] | type[BsyG] = BsyG

    def vol(self, nalb: float = 1.0):
        """Returns the volume corresponding to a number of bricks  based on their
        *Nalbanum*.  1 sar volume for 720 bricks if nalb is 1.
        Output is a ``Bvol`` object.

        :nalb: *nalbanum* in decimal e.g. 7.20 for type 2 bricks (defaul: 1.0)
        :type nalb: float

        ==========  ============  ============
        Brick type  Nalb. (dec.)  Nalb. (sex.)
        ==========  ============  ============
        1           9.00          9
        1a          8.33          8:20
        2           7.20          7:12
        3           5.40          5:24
        4           5.00          5
        5           4.80          4:48
        7           3.33          3:20
        8           2.70          2:42
        9           2.25          2:15
        10          1.875         1:52:30
        11          1.20          1:12
        12          1.00          1
        ==========  ============  ============

        """
        tt = int(self.dec / nalb)
        return Bvol(tt)
