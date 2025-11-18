from mesomath.npvs import Blen as bl  # type: ignore


def test_blen():
    a = bl("1 ninda 3 kus 7 susi")
    b = bl("1 us 8 kus 16 susi")

    assert str(a) == "1 ninda 3 kus 7 susi"
    assert str(b) == "1 us 8 kus 16 susi"
    assert a.title == "Babylonian length meassurement"
    assert b.dec == 21856
    assert a.uname == ["susi", "kus", "ninda", "us", "danna"]
    assert a.aname == "šu-si kuš3 ninda UŠ danna".split()
    assert str(a.sex()) == "7:37"
    assert str(b.sex(0)) == "6:4:16"

    assert a <= b

    assert round(a.si(), 3) == 7.617
    assert round(b.si(), 3) == 364.267
    assert b.SI() == "364.26666666666665 meters"

    assert str(a + b) == "1 us 1 ninda 11 kus 23 susi"
    assert str(a - b) == "59 ninda 5 kus 9 susi"
    assert str(b * 2) == "2 us 1 ninda 5 kus 2 susi"
    assert str(2 * a) == "2 ninda 6 kus 14 susi"

    assert str(a * b) == "77 sar 4 gin 29 se"
    assert (a * b).title == "Babylonian surface meassurement"
    assert (a * b).SI() == "2774.4966666666664 square meters"
    v = (a * b) * bl("1 kus")
    assert v.title == "Babylonian volume meassurement"
    assert v.SI() == "1387.2483333333332 cube meters"

    assert b.prtf() == "1 us 2/3 ninda 1/2 kus 1 susi"
    assert b.prtf(1, 1) == "1 UŠ 2/3 ninda 1/2 kuš3 1 šu-si"

    assert str(bl("1 kus 15 susi").metval()) == "7:30"

    bl.prtsex = True

    assert str(a) == "(1 dis) ninda (3 dis) kus (7 dis) susi"
    assert str(b) == "(1 dis) us (8 dis) kus (1 u 6 dis) susi"
    assert b.prtf(1, 1) == "(1 dis) UŠ 2/3 ninda 1/2 kuš3 (1 dis) šu-si"
    
    assert bl("(1 dis) UŠ 2/3 ninda 1/2 kuš3 (1 dis) šu-si").dec == 21856
