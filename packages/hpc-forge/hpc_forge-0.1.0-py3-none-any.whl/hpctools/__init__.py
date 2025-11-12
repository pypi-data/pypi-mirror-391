"""
HPC Tools
~~~~~~~~~~

Automation toolkit for generating Makefiles and SLURM job scripts.
Includes auxiliary modules for future extensions such as benchmarking
and performance analysis.

Subcommands:
    hpctools make   → Create an interactive Makefile
    hpctools slurm  → Create a SLURM job script
    hpctools all    → Generate both at once

(c) 2025 HPC Tools — Diogo Silva (diogocsilva12)
"""

__appname__ = "hpctools"
__version__ = "0.1.0"
__author__ = "Diogo Silva (diogocsilva12)"
__license__ = "MIT"

from hpctools.makegen import generate_makefile
from hpctools.slurmgen import generate_slurm
from hpctools.utils import success, warn, error, timestamp
