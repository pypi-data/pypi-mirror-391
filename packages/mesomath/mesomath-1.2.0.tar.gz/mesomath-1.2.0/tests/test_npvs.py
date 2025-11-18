from mesomath.npvs import Npvs as np  # type: ignore


def test_npvs():
    a = np(11111)
    assert a.__repr__() == "1 fur 4 ch 1 ft 2 hh 3 in"
    assert a.scheme() == [
        "lea",
        "<-3-",
        "mi",
        "<-8-",
        "fur",
        "<-10-",
        "ch",
        "<-22-",
        "yd",
        "<-3-",
        "ft",
        "<-3-",
        "hh",
        "<-4-",
        "in",
    ]
    assert a.scheme(True) == [
        "league",
        "<-3-",
        "mile",
        "<-8-",
        "furlong",
        "<-10-",
        "chain",
        "<-22-",
        "yard",
        "<-3-",
        "foot",
        "<-3-",
        "hand",
        "<-4-",
        "inch",
    ]
    assert a.list == [3, 2, 1, 0, 4, 1, 0, 0]

    assert str(np("1 mi") + np("70 ft")) == "1 mi 1 ch 1 yd 1 ft"
    assert str(np("1 mi") - np("70 ft")) == "7 fur 8 ch 20 yd 2 ft"
    assert a * 7.5 == 7.5 * a == np("1 mi 2 fur 5 ch 4 yd 2 ft 1 hh")
    assert str(a / 7.5) == "1 ch 19 yd 1 hh 1 in"

    assert a.si() == 282.2194
    assert a.SI() == "282.2194 meters"

    assert not a <= np(1000)
    assert  a != np(1000)
