from mesomath.npvs import Bsur as bs, Blen as bl  # type: ignore


def test_bsur():
    a = bs(111111)
    b = bs(12222)
    lon = bl("1 kus")

    assert str(a) == "10 sar 17 gin 51 se"
    assert a.SI() == "370.36999999999995 square meters"
    assert str(b) == "1 sar 7 gin 162 se"
    assert str(a + b) == "11 sar 25 gin 33 se"
    assert str(a - b) == "9 sar 9 gin 69 se"

    c = a * lon

    assert c.title == "Babylonian volume meassurement"
    assert str(c) == "10 sar 17 gin 51 se"
