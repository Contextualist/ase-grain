Implement tasklets upon base ASE tasklets
=========================================

.. module:: ase_grain.base

The base tasklets provides a backend-agnostic interface to run ASE
calculators asynchronously. To simplify the interface, we do not follow
ASE's conventions, such as Atoms object and return values' units.

Before starting to implement a tasklet for a new ASE calculators, you
might want to know what ``ASE-Grain`` tasklet is actually doing in
addition to the ASE calculator. In short, a tasklet:

1. Make running the calculation async, and
2. Make the calculation resource-aware (i.e. processors and memory)

All the other things (e.g. generate input files from a somehow uniform
parameter (atoms, method, basis, etc.) interface; run the calculation
and parse the output to get energy, forces, etc.) are handled by ASE
calculator. The first thing is nicely handled by the following base
tasklets. However, the second thing is often not so straightforward, as
backends tend to have diverse ways to define processors and memory
constraints. The existing tasklets would be a good reference for
implementing new ones.

.. autofunction:: ase_fio_task

.. autofunction:: ase_task
