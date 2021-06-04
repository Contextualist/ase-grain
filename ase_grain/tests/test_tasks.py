from ..tasks import gautask, psi4task, orcatask, qetask

from grain.subproc import subprocess_pool_scope
from grain import GVAR
from grain.resource import Node
GVAR.res = Node(N=[0,1,2,3],M=1) # 4 processors, 1 GB memory

from numpy import allclose

from pathlib import Path
import shutil

water = dict(
    chg_mlt=(0, 1),
    atcor=[[-4.546300, 0.811495, -1.302550],
           [-3.783370, 1.116810, -1.871810],
           [-3.418490, 0.344640, -2.321040]],
    ian=[1, 8, 1],
)

w6pbc = dict(
    atcor=[[2.377916, 4.607952, 2.295296],
           [2.290657, 5.170671, 3.113542],
           [3.231187, 4.118077, 2.513281],
           [4.486581, 3.424784, 3.549969],
           [5.436525, 3.193372, 3.324155],
           [4.045015, 2.580548, 3.839679],
           [3.276096, 5.768514, 4.645891],
           [2.876410, 5.334745, 5.460351],
           [4.003521, 5.137462, 4.399188],
           [2.636876, 1.304441, 4.084942],
           [2.794761, 0.313657, 4.035826],
           [2.067374, 1.511739, 3.291952],
           [7.098516, 2.734889, 3.132259],
           [7.698785, 2.851178, 3.912037],
           [7.657013, 2.831813, 2.325240],
           [1.346627, 3.172078, 1.982183],
           [1.056175, 2.224991, 1.828191],
           [1.644589, 1.919165, 1.068865]],
    ian=[8, 1, 1, 8, 1, 1, 8, 1, 1, 8, 1, 1, 8, 1, 1, 1, 8, 1],
    cell=[[8.010423,  0.938291, -0.987320],
          [0.594984,  7.205983,  0.728675],
          [0.039904, -0.296298,  4.488180]],
    kpts=[1, 1, 1],
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

async def test_qe():
    e, f = await qetask("test", pseudopotentials=dict(H="H.pbe-kjpaw.UPF", O="O.pbe-kjpaw.UPF"), **w6pbc)
    assert allclose([e], [-132.13698306697356])
    assert allclose(f, [[ 0.00507637,  0.00517378,  0.00209286],
                        [ 0.00242667, -0.00382694, -0.00267982],
                        [-0.00239504,  0.00072884,  0.00200538],
                        [ 0.00069194, -0.00564223, -0.00101254],
                        [-0.00485367,  0.00096778,  0.00123700],
                        [ 0.00284253,  0.00635662, -0.00170917],
                        [ 0.00044137, -0.00739323,  0.00168766],
                        [ 0.00194707,  0.00038896, -0.00111052],
                        [-0.00524870,  0.00314462, -0.00032727],
                        [-0.00690890, -0.00216192, -0.00149027],
                        [-0.00236904,  0.00458062,  0.00000229],
                        [ 0.00321971, -0.00021791,  0.00291159],
                        [ 0.00945597,  0.00246292, -0.00085021],
                        [-0.00284838, -0.00132355, -0.00496447],
                        [-0.00303784, -0.00058365,  0.00550625],
                        [-0.00058888, -0.00468056, -0.00020605],
                        [ 0.00448568,  0.00118818, -0.00013567],
                        [-0.00233683,  0.00083768, -0.00095703]])
    cleanup("test.pwi", "test.pwo", "pwscf.xml", "pwscf.save/")

def cleanup(*logs):
    for l in logs:
        f = Path(l)
        assert f.exists(), f"data file {l} not found"
        f.unlink() if f.is_file() else shutil.rmtree(f)
