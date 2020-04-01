Implement tasklets upon base ASE tasklets
=========================================

.. module:: ase_grain.base

The base tasklets provides a backend-agnostic interface to run ASE
calculators asynchronously. To simplify the interface, we do not follow
ASE's conventions, such as Atoms object and return values' units.

.. autofunction:: ase_fio_task

.. autofunction:: ase_task
