from ..tasks import gautask, psi4task, orcatask

from grain.subproc import subprocess_pool_scope
from grain import GVAR
from grain.resource import Node
GVAR.res = Node(N=[0,1,2,3],M=1) # 4 processors, 1 GB memory

from numpy import allclose

from pathlib import Path

import pytest

water = dict(
    chg_mlt=(0, 1),
    atcor=[[-4.546300, 0.811495, -1.302550],
           [-3.783370, 1.116810, -1.871810],
           [-3.418490, 0.344640, -2.321040]],
    ian=[1, 8, 1],
)

async def test_gau():
    e, f = await gautask("test", "b3lyp/6-31++g(d,p)", **water)
    assert allclose([e], [-76.4328776513])
    assert allclose(f, [[ 0.02518868,  0.00591134, -0.01959804],
                        [-0.02214769, -0.0036285 ,  0.01753445],
                        [-0.00304099, -0.00228284,  0.00206359]])
    cleanup("test.com", "test.log")

async def test_psi4():
    async with subprocess_pool_scope(): # only needed for Psi4
        e, f = await psi4task("test", "b3lyp/6-31++g(d,p)", **water)
        assert allclose([e], [-76.43287871145814])
        assert allclose(f, [[ 0.02518123,  0.00590826, -0.01959251],
                            [-0.02214985, -0.00362224,  0.01753743],
                            [-0.00303778, -0.0022901 ,  0.00205955]])
        # result from Psi4 1.4a3.dev63
    cleanup("test.dat")

async def test_orca():
    e, f = await orcatask("test", "b3lyp/6-31++g(d,p)", **water)
    assert allclose([e], [-76.394921967101])
    assert allclose(f, [[ 0.02509026,  0.00591112, -0.01968815],
                        [-0.02204778, -0.00364005,  0.01755853],
                        [-0.00304249, -0.00227107,  0.00212963]],
                    atol=1e-04) # For reason unknown, the force is rather erratic.
    cleanup("test.engrad", "test.gbw", "test.inp", "test.out", "test.prop", "test_property.txt")

def cleanup(*logs):
    for l in logs:
        f = Path(l)
        assert f.exists(), f"data file {l} not found"
        f.unlink()
