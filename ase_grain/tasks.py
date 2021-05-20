from . import monkey_patch
from .base import ase_fio_task, ase_task, dumb_fio_task

from ase.calculators.gaussian import Gaussian
from ase.calculators.psi4 import Psi4
from ase.calculators.espresso import Espresso
from ase.calculators.orca import ORCA

from grain import GVAR

from os import environ

async def gautask(cid, mb, chg_mlt, atcor, ian, cell=None, pbc=None, gau="g16", scrmem=0, **kwargs):
    """
    Args:
      cell (ndarray[(3,3), float] or see ASE doc):
        Unit cell size. Arg for ``ase.atoms.Atoms``
      pbc (bool or (bool, bool, bool)): Periodic
        boundary conditions along each axis. Arg for
        ``ase.atoms.Atoms``
      gau (str): the Gaussian executable
      scrmem (int): memory (in GB), out of the total
        memory allocated, for scratch dir on a memory
        fs.

    Any other keyword args are treated as Link0 or
    route keywords. See ASE's `Gaussian`_ calculator
    for reference.

    .. _Gaussian: https://wiki.fysik.dtu.dk/ase/ase/calculators/gaussian.html#parameters
    """
    mb = mb.split('/')
    ioplist = None
    if len(ian) > 50:
        ioplist = ('2/9=2000',) # Gaussian calculator relies on 'input orientation' block. Turn it on.
    calc = Gaussian(
        **__dl(cid), method=mb[0], basis=mb[1] if len(mb)>1 else None,
        charge=chg_mlt[0], mult=chg_mlt[1],
        cpu=__cs(GVAR.res.c),
        mem=f"{GVAR.res.m-scrmem}GB",
        ioplist=ioplist,
        **kwargs,
    )
    # This is done in Gaussian.calculate, but we skip it due to the patched async calculation
    calc.command = calc.command.replace('GAUSSIAN', gau)
    return await ase_fio_task(cid, calc, atcor, ian, cell, pbc)

async def psi4task(cid, mb, chg_mlt, atcor, ian):
    """:func:`psi4task` is implemented using
    ``grain.subproc.subprocify`` For notes and caveats
    refer to the base task :func:`ase_grain.base.ase_task`
    or ``subprocify``'s documentation.
    """
    m, b = mb.split('/')
    calc = Psi4(
        **__dl(cid), method=m, basis=b,
        charge=chg_mlt[0], multiplicity=chg_mlt[1],
        num_threads=GVAR.res.N, # use N threads for N cores, and subprocify handles which cores to bind
        memory=f"{getattr(GVAR.res,'m',0.5)}GB",
    )
    return await ase_task(cid, calc, atcor, ian)

async def qetask(cid, atcor, ian, cell,
                 pseudopotentials, kspacing=None, kpts=None, koffset=(0,0,0),
                 input_data=None, mpi="Open MPI", **kwargs):
    """
    QE has a very different from other backend. See ASE's
    `Espresso`_ calculator for reference.

    .. _Espresso: https://wiki.fysik.dtu.dk/ase/ase/calculators/espresso.html#ase.calculators.espresso.Espresso

    Args:
        cell (ndarray[(3,3), float]): Unit cell vectors.
            This is passed to ``ase.atoms.Atoms``
        mpi (str): Whether to use Open MPI or Intel MPI

    .. note:: Currently there is no way to impose a
       memory constraint on QE. Please measure ahead
       the memory consumption for your calculation, and
       use that value to inform the scheduler. There is
       no guarentee for QE to go over that value, so you
       might want to set a higher one.
    """
    calc = Espresso(
        **__dl(cid), input_data=input_data,
        pseudopotentials=pseudopotentials,
        kspacing=kspacing, kpts=kpts, koffset=koffset,
        **kwargs,
    )
    cpu = __cs(GVAR.res.c)
    if mpi == "Open MPI":
        para_prefix = f'mpirun -np {GVAR.res.N} --bind-to cpulist:ordered --cpu-set {cpu} '
    elif mpi == "Intel MPI":
        para_prefix = f'mpirun -np {GVAR.res.N} -genv I_MPI_PIN_PROCESSOR_LIST={cpu} '
    else:
        raise TypeError(f"Unsupported MPI type: {mpi}")
    calc.command = para_prefix + 'pw.x -in PREFIX.inp > PREFIX.out'
    return await ase_fio_task(cid, calc, atcor, ian, cell)

async def orcatask(cid, mb, chg_mlt, atcor, ian, orca="", simple="", block=""):
    """
    Args:
        orca (str): the ORCA executable
        simple (str): additional SimpleInput beside method
            and basis
        block (str): additional BlockInput beside ``pal``
            and ``maxcore``

    Per ASE's ORCA interface, the ORCA executable can also
    be set by envar ``ORCA_COMMAND``. This tasklet depends
    on OpenMPI >= 4.0 for parallelization.
    """
    m, b = mb.split('/')
    hdr = f"{m} {b} {simple}"
    blk = (
        f"%pal nprocs {GVAR.res.N} end\n"
        f"%maxcore {int(GVAR.res.m/GVAR.res.N*1024)}\n" # per core mem in MB
        f"{block}"
    )
    calc = ORCA(
        **__dl(cid), orcasimpleinput=hdr, orcablocks=blk,
        charge=chg_mlt[0], mult=chg_mlt[1],
    )
    ORCA_CMD = orca or environ.get('ORCA_COMMAND', 'orca')
    cpu = __cs(GVAR.res.c)
    calc.command = f'{ORCA_CMD} PREFIX.inp "--bind-to cpulist:ordered --cpu-set {cpu}" > PREFIX.out'
    return await ase_fio_task(cid, calc, atcor, ian)


def __dl(cid):
    cid = str(cid)
    if '/' not in cid: cid = "./"+cid
    d, l = cid.rsplit('/',1)
    return dict(directory=d, label=l)
def __cs(s):
    return ','.join(map(str,sorted(s)))
