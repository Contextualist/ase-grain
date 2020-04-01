Monkey patch: internally modified behviors
==========================================

.. module:: ase_grain

An ASE calculator assembles the parameters into input for the backend,
runs the calculation, and parses the output. We would like to take advantage
of ASE's exhaustive collection of serializers and parsers, but the only
async-incompatible part is running the calculation, the IO-dependent part.
Fortunately, many of the calculators involve staring an external binary,
and ASE convinently abstract the process into a generic subprocess calling
(those calculators inheriting from ``FileIOCalculator``). To make the
calculation cooperative we only need to provide an async subprocess call
and redirect all the calculation call to it. (For other more "tightly
bounded" calculators doing in-process call we uses ``subprocify`` instead.)

Monkey-patching (in ``monkey_patch.py``) substitutes the calculation
function with an async version with the same interface, though we cannot
simply override the original function as the way to call an async function
is different (i.e. `await`). So instead we provide the async method under
another name (``acalculate``) and override method ``calculate`` with raising
an exception in case we accidentally call it. In this semi-automatic manner,
we only need to call ``acalulate`` ourselves, and all the other serialization
and parsing process are still automated.

File ``tasks.py`` imports the monkey-patching, so all calculators inheriting
from ``FileIOCalculator`` are automactically patched. :func:`base.ase_fio_task`
uses the patched calculators.
