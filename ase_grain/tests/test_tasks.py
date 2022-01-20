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
    cleanup("test.com", "test.log", "fort.7")

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
    assert allclose([e], [-76.395066315323])
    assert allclose(f, [[ 0.02512568,  0.00594307, -0.01954676],
                        [-0.02213437, -0.00364643,  0.01749111],
                        [-0.00298438, -0.00229161,  0.00203149]],
                    atol=1e-05) # For reason unknown, the force is rather erratic.
    # result from ORCA 5.0.2
    cleanup("test.engrad", "test.gbw", "test.inp", "test.out", "test.densities", "test_property.txt")

async def test_qe():
    e, f = await qetask("test", pseudopotentials=dict(H="H.pbe-kjpaw.UPF", O="O.pbe-kjpaw.UPF"), **w6pbc)
    assert allclose([e], [-132.13698294697357])
    assert allclose(f, [[ 0.00504976,  0.00518278,  0.00208789],
                        [ 0.00241809, -0.00384409, -0.00268537],
                        [-0.00241164,  0.00072205,  0.00200264],
                        [ 0.00062692, -0.00559680, -0.00099763],
                        [-0.00484719,  0.00095787,  0.00123995],
                        [ 0.00283847,  0.00635893, -0.00171068],
                        [ 0.00040423, -0.00735159,  0.00165902],
                        [ 0.00194123,  0.00037703, -0.00111027],
                        [-0.00526679,  0.00314324, -0.00032122],
                        [-0.00691507, -0.00218046, -0.00149734],
                        [-0.00237290,  0.00457980,  0.00000541],
                        [ 0.00321371, -0.00022615,  0.00291348],
                        [ 0.00965936,  0.00250825, -0.00085634],
                        [-0.00283352, -0.00132806, -0.00493763],
                        [-0.00302046, -0.00058784,  0.00547721],
                        [-0.00060238, -0.00470906, -0.00020507],
                        [ 0.00447375,  0.00116309, -0.00011961],
                        [-0.00235555,  0.00083102, -0.00094443]],
                    atol=1e-04)
    # result from QE 7.0
    cleanup("test.pwi", "test.pwo", "pwscf.xml", "pwscf.save/")

def cleanup(*logs):
    for l in logs:
        f = Path(l)
        assert f.exists(), f"data file {l} not found"
        f.unlink() if f.is_file() else shutil.rmtree(f)
