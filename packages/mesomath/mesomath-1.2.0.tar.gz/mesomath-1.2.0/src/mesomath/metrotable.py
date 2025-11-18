"""Printing of metrological tables"""


# import's section

import argparse
from mesomath.npvs import Blen as bl
from mesomath.npvs import Bsur as bs
from mesomath.npvs import Bvol as bv
from mesomath.npvs import Bcap as bc
from mesomath.npvs import Bwei as bw
from mesomath.npvs import BsyG as bG
from mesomath.npvs import BsyS as bS


# Functions


def examplehead(
    example: int,
    met: type,
    names: list[str],
    ubase: int,
    minv: str | int,
    maxv: str | int,
    inc: str | int,
):
    """Prints a preamble for the examples"""

    print(
        f"""\nExample {example}:
        Table: {met.title}s
        ubase: {ubase} ({names[ubase]})
        From: {minv}
        To: {maxv}
        Step by: {inc}
Output follows:"""
    )


def header(
    args: argparse.Namespace,
    met: type,
    names: list[str],
    ubase: int,
    width: int = 20,
):
    """Prints header of metrological table
    
    :args: argument namespace
    :met: class of magnitude to be plotted
    :ubase: base unit
    :width: line width
    
    """
    width = int(width)
    if not args.noheader:
        print(f"\nMetrological list for {met.title}s")
        if args.verbose:
            print("  units: ", *met.scheme(met, args.academic))
            print("  cfact: ", *met.cfact)
        print(f"Base unit: {names[ubase]}\n")
        if args.verbose:
            print("Meassurement".ljust(width + 5), "Abstract".ljust(15), "Reciprocal")
            print("====================================================")
        else:
            print("Meassurement".ljust(width + 5), "Abstract".ljust(15))
            print("=========================================")


def metrolist(
    args: argparse.Namespace,
    met: type,
    names: list[str],
    ubase: int,
    minv: str | int,
    maxv: str | int,
    inc: str | int = 1,
    width: int = 20,
):
    """Prints a section of the metrological list for the met class.

    :args: argument namespace
    :met: class or quantity
    :ubase: base unit for the metrological list
    :minv: minimum value of the variable to print
    :maxv: maximum value of the variable to print
    :inc: variable increment or step
    :width: width reserved for printing the variable (default: 20)
    
    """

    mc = m = met(minv)
    maxv = maxv.split(",")
    inc = inc.split(",")
    for i in range(len(maxv)):
        if i > 0:
            m -= mc
            print("---------------------------------------------------")
        mb = met(maxv[i])
        mc = met(inc[i])
        #        m += mc
        while m <= mb:
            pp = m.sex(ubase)
            #            print('fractions: ',args.fractions)
            if args.fractions < 0:
                if args.verbose:
                    if pp.isreg:
                        print(str(m).ljust(width), " -> ", str(pp).ljust(15), pp.rec())
                    else:
                        print(
                            str(m).ljust(width), " -> ", str(pp).ljust(15), "--igi nu--"
                        )
                else:
                    print(str(m).ljust(width), " -> ", str(pp).ljust(15))
            else:
                if args.verbose:
                    if pp.isreg:
                        print(
                            (m.prtf(args.fractions, args.academic)).ljust(width),
                            " -> ",
                            str(pp).ljust(15),
                            pp.rec(),
                        )
                    else:
                        print(
                            (m.prtf(args.fractions, args.academic)).ljust(width),
                            " -> ",
                            str(pp).ljust(15),
                            "--igi nu--",
                        )
                else:
                    print(
                        (m.prtf(args.fractions, args.academic)).ljust(width),
                        " -> ",
                        str(pp).ljust(15),
                    )

            m += mc


def gen_parser() -> argparse.ArgumentParser:
    """User interface parser"""
    # Option definitions

    DESC = """Prints an excerpt of a metrological table"""
    EPIL = "jccsvq fecit, 2025. Public domain."

    parser = argparse.ArgumentParser(
        description=DESC,
        epilog=EPIL,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-t",
        "--type",
        help="Type of metrological table to print (Try: -r for a remainder)",
        choices=["L", "Lh", "S", "V", "C", "W", "SysG", "SysS"],
        default=None,
    )
    parser.add_argument(
        "-m",
        "--min",
        help='Minimun value of variable to print, ex: "10 susi"',
        default=1,
    )
    parser.add_argument(
        "-M",
        "--max",
        help='Maximun value of variable to print, ex:"2 kus", or a comma \
        separated list "2 kus,5 kus"',
        default=10,
    )
    parser.add_argument(
        "-i",
        "--increment",
        help='Increment of the variable between table lines, ex: "5 susi" or a \
        comma separated list matching MAX  in length "5 susi,1 kus"',
        default=1,
    )
    parser.add_argument(
        "-w",
        "--width",
        help="Sets the reserved width for printing measurement values ​​to WIDTH",
        default=20,
    )
    parser.add_argument(
        "-f", "--force", help="Force base unit to number FORCE", default=-1
    )
    parser.add_argument(
        "-x",
        "--example",
        help="Runs an example test",
        choices=["1", "2", "3", "4"],
        default=None,
    )
    parser.add_argument(
        "-n",
        "--noheader",
        help="Suppress header printing (for chaining results)",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="More information in the header and reciprocals if the abstract \
        numbers are regular",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-r",
        "--remainder",
        help="List the available measurement systems and their units, then exits",
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
        "-a",
        "--academic",
        help="With [-F|--fractions] or [-r|--remainder] uses the academic names of units.",
        action="store_true",
        default=False,
    )

    return parser


def main():
    """Entry point to metrotable"""
    # Options parsing
    parser = gen_parser()
    args = parser.parse_args()

    # Remainder section
    if args.remainder:
        print("\nRemainder of systems and units: Old Babylonian Period")
        print("=======================================================")
        print("System L: ", bl.title + "s")
        print("    Units: ", *bl.scheme(bl, args.academic))
        print("    Base unit: ", bl.uname[bl.ubase])
        print("System Lh: ", bl.title + "s (Heights)")
        print("    Units: ", *bl.scheme(bl, args.academic))
        print("    Base unit: ", bl.uname[1])
        print("System S: ", bs.title + "s")
        print("    Units: ", *bs.scheme(bs, args.academic))
        print("    Base unit: ", bs.uname[bs.ubase])
        print("System V: ", bv.title + "s")
        print("    Units: ", *bv.scheme(bv, args.academic))
        print("    Base unit: ", bv.uname[bv.ubase])
        print("System C: ", bc.title + "s")
        print("    Units: ", *bc.scheme(bc, args.academic))
        print("    Base unit: ", bc.uname[bc.ubase])
        print("System W: ", bw.title + "s")
        print("    Units: ", *bw.scheme(bw, args.academic))
        print("    Base unit: ", bw.uname[bw.ubase])
        print("NPVN System S: ", bS.title)
        print("    Units: ", *bS.scheme(bS, args.academic))
        print("    Base unit: ", bS.uname[bS.ubase])
        print("NPVN System G: ", bG.title)
        print("    Units: ", *bG.scheme(bG, args.academic))
        print("    Base unit: ", bG.uname[bG.ubase])
        exit()

    if (args.type is None) and (args.example is None):
        print("Nothing to do, exiting!")
        exit()

    # Examples section; initialization
    args.force = int(args.force)
    if args.force >= 0:
        ubase = args.force
    else:
        ubase = 2

    # Examples section; definitions
    if args.example == "1":
        example = 1
        met = bl
        minv = "10 susi"
        maxv = "2 kus"
        inc = "5 susi"
    if args.example == "2":
        example = 2
        met = bs
        minv = "10 gin"
        maxv = "2 sar"
        inc = "10 gin"
    if args.example == "3":
        example = 3
        met = bc
        minv = "1 gur"
        maxv = "3 gur"
        inc = "3 ban"
    if args.example == "4":
        example = 4
        met = bl
        minv = "10 susi"
        maxv = "2 kus,12 kus,5 ninda"
        inc = "5 susi,1 kus,6 kus"
    if args.example:
        if args.academic:
            names = met.aname
        else:
            names = met.uname

    # Examples section; execution
    if args.example is not None:
        width = int(args.width)
        examplehead(example, met, names, ubase, minv, maxv, inc)
        header(args, met, names, ubase, width)
        metrolist(args, met, names, ubase, minv, maxv, inc, width)
        exit()

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
    if args.type == "Lh":
        ubase = 1
    else:
        ubase = met.ubase
    if args.pedantic and not any([met == bS, met == bG]):
        met.prtsex = True
    #        print('Pedantic!')
    if args.academic:
        names = met.aname
    else:
        names = met.uname

    minv = args.min
    maxv = args.max
    inc = args.increment
    width = int(args.width)
    if args.force >= 0:  # Force ubase to given value
        ubase = args.force

    # Executing
    header(args, met, names, ubase, width)
    metrolist(args, met, names, ubase, minv, maxv, inc, width)
    exit()


if __name__ == "__main__":
    main()
