"""Generates list of Hamming's numbers in three formats

Hamming numbers are numbers of the form

|    H = 2^i × 3^j × 5^k
|       where
|    i,  j,  k  ≥  0

Here we use the cyclic generator, method #2, from
https://rosettacode.org/wiki/Hamming_numbers#Python
adapted to ``Python3``.

Formats:
--------

| Python list, function: ``hamming(a,b=none)``
| CSV, function: ``genCSV(maxn, sep = ",")``
| SQL, function: ``genSQL(maxn)``

You can use ``sqlite3`` command line shell utility (https://www.sqlite.org/download.html) to generate the ``regular.db3`` ``sqlite3`` database required by ``BabN`` class in this way:

    ``$ python3 hamming.py |sqlite3 regular.db3``

All output goes to stdout

jccsvq fecit 2025
"""

from itertools import islice, chain, tee
from mesomath.babn import BabN



def merge(r, s):
    """Internal function

    :meta private:
    """
    # This is faster than heapq.merge.
    rr = r.__next__()
    ss = s.__next__()
    while True:
        if rr < ss:
            yield rr
            rr = r.__next__()
        else:
            yield ss
            ss = s.__next__()


def p(n):
    """Internal function

    :meta private:
    """

    def gen():
        x = n
        while True:
            yield x
            x *= n

    return gen()


def pp(n, s):
    """Internal function

    :meta private:
    """

    def gen():
        for x in merge(s, chain([n], (n * y for y in fb))):
            yield x

    r, fb = tee(gen())
    return r


def hamming(a: int, b: int | None = None) -> list[int]:
    """Generates a list of Hamming's numbers

    :a and b: generates the list from a to b if b is not None, otherwise return a list containig the a-th hamming number only

    """
    if not b:
        b = a + 1
    seq = chain([1], pp(5, pp(3, p(2))))
    return list(islice(seq, a - 1, b - 1))


def genCSV(maxn: int, sep: str = ",") -> None:
    """Generates csv table of regular numbers and reciprocals

    genCSV(80000) takes a few seconds!
    writes to stdin
    | maxn: decimal int, write the table up to this value
    |  sep: csv field separator (default: ",")"""
 
    rlist = hamming(1, maxn)
    i = 0
    BabN.fill = True
    for x in rlist:
        if x % 60 != 0:
            i += 1
            n = BabN(x)
            r = n.rec()
            print(i, n.dec, n, n.len(), r.dec, r, sep=sep)


if __name__ == "__main__":

    def genSQL(maxn: int) -> None:
        """Generates list or regular numbers in sqlite3 SQL format
        | maxn: decimal int, write the table up to this value"""
        rlist = hamming(1, maxn)
        i = 0
        BabN.fill = True
        print(sqlhead)
        for x in rlist:
            if x % 60 != 0:
                i += 1
                n = BabN(x)
                print(f"INSERT INTO regulars VALUES({i},'{n}',{n.len()});")
        print(sqltail)

    if __name__ == "__main__":
        sqlhead = """PRAGMA foreign_keys=OFF;
    BEGIN TRANSACTION;
    CREATE TABLE  IF NOT EXISTS regulars (
	    id INTEGER PRIMARY KEY,
        regular    TEXT,
        len     INTEGER
    );
    """

        sqltail = """CREATE UNIQUE INDEX regs ON regulars (regular);
    COMMIT;
    """

        genSQL(79405)
