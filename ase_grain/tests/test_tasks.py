from ..tasks import gautask, psi4task

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
        assert allclose(f, [[ 0.0251815 ,  0.00590822, -0.01959273],
                            [-0.02215968, -0.00362866,  0.01754429],
                            [-0.00303764, -0.00228981,  0.00205949]])
    cleanup("test.dat")

def cleanup(*logs):
    for l in logs:
        f = Path(l)
        assert f.exists(), f"data file {l} not found"
        f.unlink()
