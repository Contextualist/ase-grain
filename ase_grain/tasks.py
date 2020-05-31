import ase_grain.monkey_patch
from .base import ase_fio_task, ase_task, dumb_fio_task

from ase.calculators.gaussian import Gaussian
from ase.calculators.psi4 import Psi4
#from ase.calculators.espresso import Espresso
from ase.calculators.orca import ORCA

from grain import GVAR

from os import environ

async def gautask(cid, mb, chg_mlt, atcor, ian, gau="g16"):
    """
    Args:
        gau (str): the Gaussian executable
    """
    mb = mb.split('/')
    ioplist = None
    if len(ian) > 50:
        ioplist = ('2/9=2000',) # Gaussian calculator relies on 'input orientation' block. Turn it on.
    calc = Gaussian(
        **__dl(cid), method=mb[0], basis=mb[1] if len(mb)>1 else None,
        charge=chg_mlt[0], mult=chg_mlt[1],
        cpu=','.join(map(str,sorted(GVAR.res.c))),
        mem=f"{GVAR.res.m}GB",
        ioplist=ioplist,
    )
    # This is done in Gaussian.calculate, but we skip it due to the patched async calculation
    calc.command = calc.command.replace('GAUSSIAN', gau)
    return await ase_fio_task(cid, atcor, ian, calc)

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
    return await ase_task(cid, atcor, ian, calc)

async def qetask(cid, mb, chg_mlt, atcor, ian):
    raise NotImplementedError
    calc = Espresso(
        **__dl(cid),
    )
    return await ase_fio_task(cid, atcor, ian, calc)

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
    cpu = ','.join(map(str,sorted(GVAR.res.c)))
    calc.command = f'{ORCA_CMD} PREFIX.inp "--bind-to cpulist:ordered --cpu-set {cpu}" > PREFIX.out' # TODO: this is for mpirun 4.0; generalize it to 3.x
    return await ase_fio_task(cid, atcor, ian, calc)


def __dl(cid):
    if '/' not in cid: cid = "./"+cid
    d, l = cid.rsplit('/',1)
    return dict(directory=d, label=l)
