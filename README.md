# ASE-Grain

[![Docs](https://img.shields.io/badge/docs-read%20now-blue.svg)](https://ase-grain.readthedocs.io)
[![PyPI version](https://img.shields.io/pypi/v/ase-grain.svg)](https://pypi.org/project/ase-grain)

An async wrapper for [ASE](https://gitlab.com/ase/ase), adapting the calculators into Grain-compatible jobs.

### Supported calculators

* Gaussian
* Psi4
* ORCA
* Quantum Espresso

### Quickstart

```Bash
pip install ase-grain
```

Want to try out the tasklets without running a Grain mission? Easy:

```Python
from ase_grain import gautask, psi4task

from grain.subproc import subprocess_pool_scope
from grain import GVAR
from grain.resource import Node

import trio

async def main():
    async with subprocess_pool_scope(): # only needed for Psi4
        GVAR.res = Node(N=[0,1,2,3],M=1) # 4 processors, 1 GB memory
        e, f = await psi4task("test", "b3lyp/6-31++g(d,p)", 
        #e, f = await gautask("test", "b3lyp/6-31++g(d,p)",
            (0, 1),
            [[-4.546300, 0.811495, -1.302550],
             [-3.783370, 1.116810, -1.871810],
             [-3.418490, 0.344640, -2.321040]],
            [1, 8, 1], # a water molecule
        )
        print(e)
        print(f)

trio.run(main)
```

This also demonstrates that you can use `ASE-Grain` outside a Grain scheduler, more specifically, in any Trio-based async environment with Grain's context variables (`GVAR`).
