"""Prints Babylonian/sexagesimal multiplication tables"""

# import's section

import argparse
from mesomath.babn import BabN as bn
from typing import Final


# Functions
def multable(
    n: int | str,
    pral: bool = True,
    sep: str = ":",
    fill: bool = False,
) -> None:
    """Returns the n multiplication table for principal numbers or for all

    :n: decimal integer < 60
    :pral: if True writes the table for principal numbers:
          [i+1 for i in range(20)]+[30,40,50]
          if False writes the table for:
          [i+1 for i in range(59)]
          (default: True)
    :sep: sexagesimal digits separator (default: ":")
    :pad: add left zero to sexagesimal digits <= 9 (default: False)

    """
    oldsep: str = bn.sep
    oldfill: bool = bn.fill
    bn.sep = sep
    bn.fill = fill
    if isinstance(n, int):
        nn = n
    elif isinstance(n, str):
        nn = bn(n).dec
    if pral:
        pnum = [i + 1 for i in range(20)] + [30, 40, 50]
    else:
        pnum = [i + 1 for i in range(59)]
    print("\n  i", ("i * " + str(n)).rjust(20), "\n =======================")
    for i in pnum:
        print(f" {i:2d} {str(bn(nn * i)).rjust(20)}")
    bn.sep = oldsep
    bn.fill = oldfill


def listtables() -> None:
    """Lists multipliers traditionally used by Babylonian scribes."""
    a: Final[list[str]] = (
        "50 45 44:26:40 40 36 30 25 24 22:30 20 18 16:40 16 15 12:30 12"
        + " 10 9 8:20 8 7:30 7:12 7 6:40 6 5 4:30 4 3:45 3:20 3 2:30 2:24 2 1:40"
        + " 1:30 1:20 1:15"
    ).split()

    print("List of multipliers:\n")
    for i in a:
        if i == "7":
            print(7)
        else:
            tt = bn(i)
            print(str(tt).ljust(8), str(tt.rec()).rjust(6))


def gen_parser() -> argparse.ArgumentParser:
    """User interface parser"""
    DESC = """Prints Babylonian multiplication tables."""
    EPIL = "jccsvq fecit, 2025. Public domain."

    # Option definitions
    parser = argparse.ArgumentParser(
        description=DESC,
        epilog=EPIL,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "mult",
        type=str,
        help="Multiplier, use 0 for a list of multiplication tables used in\
         scribal learning",
        default="1",
    )
    parser.add_argument(
        "-s", "--separator", type=str, help="Sexagesimal digit separator", default=":"
    )
    parser.add_argument(
        "-p",
        "--principal",
        help="Use only principal numbers",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-f", "--fill", help="Pad with zeros", action="store_true", default=False
    )

    return parser


def main():
    """Module entry point"""
    # Option parsing
    parser = gen_parser()
    args = parser.parse_args()

    # executing
    if args.mult == "0":
        listtables()
    else:
        multable(args.mult, pral=args.principal, sep=args.separator, fill=args.fill)


if __name__ == "__main__":
    main()
