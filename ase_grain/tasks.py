import ase_grain.monkey_patch
from .base import ase_fio_task, ase_task, dumb_fio_task

from ase.calculators.gaussian import Gaussian
from ase.calculators.psi4 import Psi4
#from ase.calculators.espresso import Espresso
from ase.calculators.orca import ORCA

from grain import GVAR

async def gautask(cid, mb, chg_mlt, atcor, ian, gau="g16"):
    """
    Args:
        gau (str): the Gaussian executable
    """
    m, b = mb.split('/')
    calc = Gaussian(
        **__dl(cid), method=m, basis=b,
        charge=chg_mlt[0], mult=chg_mlt[1],
        cpu=','.join(map(str,sorted(GVAR.res.c))),
        mem=f"{GVAR.res.m}GB",
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
        num_threads=GVAR.res.N, # use N threads for N cores
        memory=f"{getattr(GVAR.res,'m',0.5)}GB",
    )
    return await ase_task(cid, atcor, ian, calc)

async def qetask(cid, mb, chg_mlt, atcor, ian):
    raise NotImplementedError
    calc = Espresso(
        **__dl(cid),
    )
    return await ase_fio_task(cid, atcor, ian, calc)

async def orcatask(cid, mb, chg_mlt, atcor, ian):
    #raise NotImplementedError
    m, b = mb.split('/')
    hdr = f"{m} {b}"
    blk = '\n'.join([
        f"%pal nprocs {GVAR.res.N} end", # FIXME: bind to specific processor, use MPI --bind-to
        f"%maxcore {int(GVAR.res.m*1024)} end", # in MB
    ])
    calc = ORCA(
        **__dl(cid), orcasimpleinput=hdr, orcablocks=blk,
        charge=chg_mlt[0], mult=chg_mlt[1],
    )
    return await dumb_fio_task(cid, atcor, ian, calc)
    #return await ase_fio_task(cid, atcor, ian, calc)


def __dl(cid):
    if '/' not in cid: cid = "./"+cid
    d, l = cid.rsplit('/',1)
    return dict(directory=d, label=l)
