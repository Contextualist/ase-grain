from ase.data import atomic_masses

from contextlib import ContextDecorator
from timeit import default_timer as timer

def timeblock(text="this block", enter=False):
    class TimeblockCtx(ContextDecorator):
        def __enter__(self):
            self.st = timer()
            if enter:
                print(f"[{self.st:.3f}]\tEnter {text}")
            return self
        def __exit__(self, *exc):
            et = timer()
            print(f"[{et:.3f}]\tTime elapsed for {text}{' (incomplete)' if any(exc) else ''}: {et-self.st}")
            return False
    return TimeblockCtx()

def water_charge(ian):
    """Calculate charge for a water cluster's fragment.
    Assign +1 for H and -2 for O.

    Args:
        ian (ndarray[(N,), int]): Atomic numbers

    Returns:
        charge in int
    """
    return sum({ 1:+1, 8:-2 }[i] for i in ian)

def center_of_mass(acoords, ian):
    """Calculate the center of mass for a group of atoms.

    Args:
        acoords (ndarray[(N,3), float]): Atoms' coordinates
        ian (ndarray[(N,), int]): Atomic numbers

    Returns:
        coordinate for the center of mass
        (ndarray[(3,), float])
    """
    m = atomic_masses[ian]
    return m @ acoords / sum(m)
