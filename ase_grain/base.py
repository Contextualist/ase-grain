from grain.subproc import subprocify

async def ase_fio_task(cid, calc, atcor, ian, cell=None, pbc=None):
    """Base task for calculators implementing the
    `FileIOCalculator`_ interface (e.g. Gaussian,
    Orca, QE).

    .. _FileIOCalculator: https://gitlab.com/ase/ase/-/blob/master/ase/calculators/calculator.py

    Class ``FileIOCalculator`` is patched to enable
    async calculation through async subprocess. See
    ``monkey_patch.py`` for details.

    Args:
      cid (str): Calculation ID, for time record only
      calc: The calculator instance
      atcor (ndarray[(N,3), float]): Atom coordinate
      ian (ndarray[(N,), int]): Atomic numbers 
      pbc (bool or (bool, bool, bool)): Periodic
        boundary conditions along each axis. Arg for
        ``ase.atoms.Atoms``
      cell (ndarray[(3,3), float] or see ASE doc):
        Unit cell size. Arg for ``ase.atoms.Atoms``

    Returns:
      Energy (in hartree) and forces (in hartree/angstrom)

    .. note:: Any task calling this should make
       sure that the calculator itself's ``calculate``
       method get handled, as this only takes care
       of ``FileIOCalculator.calculate``.
    """
    from ase.atoms import Atoms
    from ase.units import Hartree as hart2ev, Bohr as b2a
    from .util import timeblock
    mol = Atoms(numbers=ian, positions=atcor, cell=cell, pbc=pbc)
    mol.calc = calc
    with timeblock(cid):
        await mol._calc.acalculate(mol, ['energy', 'forces'], [])
    return (
        mol.get_potential_energy() / hart2ev,
        mol.get_forces() * b2a / hart2ev,
    )

async def dumb_fio_task(cid, calc, atcor, ian, cell=None, pbc=None):
    import numpy as np
    from ase.atoms import Atoms
    mol = Atoms(numbers=ian, positions=atcor, cell=cell, pbc=pbc)
    mol.calc = calc
    mol._calc.write_input(mol, ['energy', 'forces'], [])
    return (
        0.0,
        np.zeros_like(atcor),
    )

@subprocify
def ase_task(cid, calc, atcor, ian):
    """Base task for inproc calculators (e.g. Psi4).

    For Parameters and Returns see above :func:`ase_fio_task`.

    :func:`ase_task` uses ``grain.subproc.subprocify``
    to "asyncify" the calculator, as we assume that an
    inproc calculator's ``calculate`` method is CPU
    intensive. ``subprocify`` requires an async
    context to maintain a subprocess pool. This could
    be simply achieved by::

      from grain.subproc import subprocess_pool_scope
      async with subprocess_pool_scope():
          # Safely call subprocified functions within

    .. note:: Task calling this experiences an overhead
       for the first few runs due to ``subprocify``'s
       subprocess startup cost, which will be amortized
       later as the subprocesses are reused.
    """
    from ase.atoms import Atoms
    from ase.units import Hartree as hart2ev, Bohr as b2a
    from .util import timeblock
    mol = Atoms(numbers=ian, positions=atcor)
    mol.calc = calc
    with timeblock(cid):
        mol._calc.calculate(mol, ['energy', 'forces'], [])
    return (
        mol.get_potential_energy() / hart2ev,
        mol.get_forces() * b2a / hart2ev,
    )
