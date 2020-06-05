.. ASE-Grain documentation master file, created by
   sphinx-quickstart on Sat Mar 28 01:11:28 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

ASE-Grain: An async wrapper for ASE
===================================

ASE-Grain encapsulates the
`ASE calculators <https://wiki.fysik.dtu.dk/ase/ase/calculators/calculators.html>`__
into tasklets, a single async function call that calculates energy and forces
for a molecule using a electronic structure calculation backend. ASE provides
interface to dozens of backends. Currently ASE-Grain supports Gaussian, Psi4, ORCA,
and Quantum Espresso, but other backend can be easily "asyncified" and added. The
tasklets are designed to be used with Grain scheduler, but can also be easily
repurposed for other async integrations.

To get started, go through the tasklets and pick the one for the calculation backend
of your choice. The tasklets are resource-aware and can be submited as a Grain
job.

To develop tasklet for a new calculation backend from ASE, or to learn more
about the internals, check out base tasklets and monkey patch.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   tasks.rst
   util.rst
   base.rst
   monkey_patch.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
