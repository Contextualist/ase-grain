Grain-ready tasklets
====================

.. module:: ase_grain.tasks

General interface ::

    async def Xtask(
        cid:     str,                   # calculation id (input, log files name after it)
        mb:      str,                   # "{method}/{basis}"
        chg_mlt: (int, int),            # charge and multiplicity
        atcor:   ndarray[(N,3), float], # atom coordinates
        ian:     ndarray[(N,), int],    # corresponding atomic number
        ...
    ) -> (energy: float, forces: ndarray[(N,3), float])

The energy is in hartree and forces in hartree/angstrom. The following
reference lists additional parameters specific to each backend.

.. autofunction:: gautask

.. autofunction:: psi4task

.. autofunction:: orcatask

.. autofunction:: qetask
