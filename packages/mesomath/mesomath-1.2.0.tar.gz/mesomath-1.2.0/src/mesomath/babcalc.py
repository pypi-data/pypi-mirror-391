import code
import sys

from mesomath.__about__ import __version__ as VERSION

from mesomath.babn import BabN as bn  # noqa: F401
from mesomath.npvs import Blen as bl  # noqa: F401
from mesomath.npvs import Bsur as bs  # noqa: F401
from mesomath.npvs import Bvol as bv  # noqa: F401
from mesomath.npvs import Bcap as bc  # noqa: F401
from mesomath.npvs import Bwei as bw  # noqa: F401
from mesomath.npvs import BsyG as bG  # noqa: F401
from mesomath.npvs import BsyS as bS  # noqa: F401
from mesomath.npvs import Bbri as bb  # noqa: F401

message = f"""\nWelcome to Babylonian Calculator {VERSION}
    ...the calculator that every scribe should have!

Use: bn(number) for sexagesimal calculations
Metrological classes: bl, bs, bv, bc, bw, bG, bS and bb loaded.
Use exit() or Ctrl-D (i.e. EOF) to exit

jccsvq fecit, 2025."""

sys.ps1 = '--> '

def main():
    """Entry point for babcalc"""

    local_vars = globals().copy()  # Start with all global variables
    local_vars.update(locals())  # Add all local variables at this point

    code.interact(
        banner=message,
        local=local_vars,
        exitmsg="\n--- Exiting Babylonian Calculator, Bye! ---\n",
    )


if __name__ == "__main__":
    main()
