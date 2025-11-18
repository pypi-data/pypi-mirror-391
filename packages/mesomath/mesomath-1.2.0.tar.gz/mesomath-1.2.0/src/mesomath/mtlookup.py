"""Lookups in metrological tables"""

# import's section
import argparse
from mesomath.babn import BabN as bn
from mesomath.npvs import Blen as bl
from mesomath.npvs import Bsur as bs
from mesomath.npvs import Bvol as bv
from mesomath.npvs import Bcap as bc
from mesomath.npvs import Bwei as bw
from mesomath.npvs import BsyG as bG
from mesomath.npvs import BsyS as bS


def gen_parser() -> argparse.ArgumentParser:
    """User interface parser"""
    # Option definitions

    DESC = """Prints abstract number corresponding to a meassure or lists 
    measures having an abstract number."""
    EPIL = "jccsvq fecit, 2025. Public domain."

    parser = argparse.ArgumentParser(
        description=DESC,
        epilog=EPIL,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-t",
        "--type",
        help="Metrology to use",
        choices=["L", "Lh", "S", "V", "C", "W", "SysG", "SysS"],
        default=None,
    )
    parser.add_argument("VALUE", type=str, help="Value ")
    parser.add_argument(
        "-r",
        "--reverse",
        help="Reverse lookup ,lists measures having an abstract number",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-f", "--force", help="Force base unit to number FORCE", default=-1
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Prints more information",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-F",
        "--fractions",
        help="Use fractions, -F 1 to include 1/6",
        type=int,
        choices=[0, 1],
        default=-1,
    )
    parser.add_argument(
        "-p",
        "--pedantic",
        help="Write the coefficients of the units in the measurements using the\
         S and G Systems",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-s",
        "--strict",
        help="Suppress partial matches in reverse lookup.",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-a",
        "--academic",
        help="With [-F|--fractions] or [-r|--remainder] uses the academic names of units.",
        action="store_true",
        default=False,
    )

    return parser


def main():
    """Entry point to mtlookup"""
    # Options parsing
    parser = gen_parser()
    args = parser.parse_args()

    # Main section; selecting classes and defining default table ubase
    if args.type == "L":
        met = bl
    elif args.type == "Lh":
        met = bl
    elif args.type == "S":
        met = bs
    elif args.type == "V":
        met = bv
    elif args.type == "C":
        met = bc
    elif args.type == "W":
        met = bw
    elif args.type == "SysG":
        met = bG
    elif args.type == "SysS":
        met = bS
    else:
        exit()

    ubase = met.ubase
    if args.type == "Lh":
        ubase = 1
    if int(args.force) >= 0:
        ubase = int(args.force)
    if args.pedantic and not any([met == bG, met == bS]):
        met.prtsex = True

    # executing

    if args.reverse:
        a = args.VALUE
        aa = bn(a)
        adec = aa.dec
        x = adec * met.cfact[ubase]
        print("\nLooking for ", met.title + "s with abstract = ", a)
        print("    Base unit: ", met.uname[ubase])
        print("========================================================")
        for i in range(-3, 5):
            x1 = int(x // 60**i)
            if x1 >= 1:
                if args.fractions < 0:
                    y = met(x1)
                else:
                    y = met(x1).prtf(args.fractions, args.academic)
                    y0 = met(x1)
                pp = met(x1).sex(ubase)
                if args.strict:
                    if str(aa) == str(pp):
                        if args.verbose:
                            print(y, "\n    Equiv.: ", y0.SI(), "\n    Abstract: ", pp)
                        else:
                            print(y, " <- ", pp)
                else:
                    if args.verbose:
                        print(y, "\n    Equiv.: ", y0.SI(), "\n    Abstract: ", pp)
                    else:
                        print(y, " <- ", pp)

            else:
                break
        exit()

    m = args.VALUE
    try:
        m = int(m)
    except Exception:
        pass
    finally:
        aa = met(m)
    if args.fractions < 0:
        y = aa
    else:
        y = aa.prtf(args.fractions, args.academic)

    pp = aa.sex(ubase)
    if args.verbose:
        print("\nAbstract number for ", met.title)
        print("    Base unit: ", met.uname[ubase])
        print("========================================================")
        if pp.isreg:
            print(y, " -> ", pp, "Reciprocal: ", pp.rec())
        else:
            print(y, " -> ", pp, "Reciprocal: ", "--igi nu--")
    else:
        print(y, " -> ", pp)


if __name__ == "__main__":
    main()
