"""Fail unless fpr_ff1 and its compiled extension import from an installed wheel.

Run with the interpreter of the clean environment the wheel was installed
into, from the repository checkout (plan 00007 STEP-06, review 00008
MED-02).  A job that tests the checkout's ``src/`` while a wheel sits
installed beside it looks green and proves nothing about the published
artifact -- the failure class review 00006 MAJ-01 was about.  This check is
what makes the installed-wheel jobs trustworthy; never relax it to get a job
green.
"""

import importlib.resources
import pathlib
import sys
import sysconfig
from importlib.metadata import version

import fpr_ff1._rs as rs

import fpr_ff1


def _say(line: str) -> None:
    sys.stdout.write(line + "\n")


checkout_src = (pathlib.Path.cwd() / "src").resolve()
purelib = pathlib.Path(sysconfig.get_paths()["purelib"]).resolve()
package = pathlib.Path(fpr_ff1.__file__).resolve()
extension = pathlib.Path(rs.__file__).resolve()

_say(f"fpr_ff1     -> {package}")
_say(f"fpr_ff1._rs -> {extension}")
_say(f"site-packages: {purelib}")

for label, path in (("fpr_ff1", package), ("fpr_ff1._rs", extension)):
    if path.is_relative_to(checkout_src):
        raise SystemExit(f"{label} imported from the checkout ({path}), not the installed wheel")
    if not path.is_relative_to(purelib):
        raise SystemExit(f"{label} imported from {path}, outside {purelib}")

# The distribution's own extension: abi3 on POSIX (_rs.abi3.so), .pyd on Windows.
if not (extension.suffix == ".pyd" or extension.name.endswith(".abi3.so")):
    raise SystemExit(f"unexpected extension file {extension.name}; expected an abi3 build")

if not importlib.resources.files("fpr_ff1").joinpath("py.typed").is_file():
    raise SystemExit("py.typed is missing from the installed wheel")

if fpr_ff1.__version__ != version("fpr-ff1"):
    raise SystemExit(f"fpr_ff1.__version__ {fpr_ff1.__version__} != {version('fpr-ff1')}")

_say(f"import origin: installed wheel, fpr-ff1 {fpr_ff1.__version__}, _rs {rs.__version__}")
