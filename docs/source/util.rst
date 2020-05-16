Misc utils
==========

.. module:: ase_grain.util

.. autofunction:: water_charge

.. autofunction:: center_of_mass

This library represents all atoms in atomic numbers. You may find ASE's
conversion utils helpful. ::

	>>> from ase.symbols import symbols2numbers
	>>> symbols2numbers(['H','O','H'])
	[1, 8, 1]
	>>> symbols2numbers("HOH")
	[1, 8, 1]
	>>> from ase.data import atomic_numbers
	>>> atomic_numbers['O']
	8
