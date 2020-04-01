"""Monkey-patch FileIOCalculator to enable async calculation.
Some other opionionate tweaks are included.
"""
from ase.calculators.calculator import *
import trio


# Function call cascade (take Gaussian as an example):
# Gaussian/Calc.get_property ->
# Gaussian.calculate(atoms, [name], system_changes) ===
# Gaussian.calculate(Gaussian.atoms, [name], []) "given no system_changes"

# The original method was to ensure `self.directory` exists on fs, which we don't care.
def FileIOCalculator__write_input(self, atoms, properties=None, system_changes=None):
    pass

def FileIOCalculator__calculate(self, *args, **kwargs):
    raise TypeError(
         "FileIOCalculator's sync calculate function should never be triggered. "
        f"Call `await self.acalculate({', '.join(map(str,args))}, {', '.join(str(k)+'='+str(v) for k,v in kwargs)})` "
         "before accessing any calculation result/property."
    )

# adapted from https://gitlab.com/ase/ase/-/blob/02c57173e032d31dd88aea005a3787475d017752/ase/calculators/calculator.py
async def FileIOCalculator__acalculate(self, atoms=None, properties=['energy'],
                                      system_changes=all_changes):
    Calculator.calculate(self, atoms, properties, system_changes)
    self.write_input(self.atoms, properties, system_changes)
    if self.command is None:
        raise CalculatorSetupError(
            'Please set ${} environment variable '
            .format('ASE_' + self.name.upper() + '_COMMAND') +
            'or supply the command keyword')
    command = self.command
    if 'PREFIX' in command:
        command = command.replace('PREFIX', self.prefix)

    try:
        #proc = subprocess.Popen(command, shell=True, cwd=self.directory)
        cproc = await trio.run_process(command, check=False, shell=True, cwd=self.directory)
    except OSError as err:
        # Actually this may never happen with shell=True, since
        # probably the shell launches successfully.  But we soon want
        # to allow calling the subprocess directly, and then this
        # distinction (failed to launch vs failed to run) is useful.
        msg = 'Failed to execute "{}"'.format(command)
        raise EnvironmentError(msg) from err

    #errorcode = proc.wait()
    errorcode = cproc.returncode

    if errorcode:
        # NOTE: we don't care about directory
        #path = os.path.abspath(self.directory)
        #msg = ('Calculator "{}" failed with command "{}" failed in '
        #       '{} with error code {}'.format(self.name, command,
        #                                      path, errorcode))
        msg = (f'Calculator "{self.name}" failed with command "{command}" '
               f'failed with error code {errorcode}')
        raise CalculationFailed(msg)

    self.read_results()

# get rid of the annoying .ase parameter file
def Parameters__write(self, filename):
    pass

# Make set_psi4 executed only once
def Psi4__init(self, *args, **kwargs):
    Calculator.__init__(self, *args, **kwargs)
    import psi4
    self.psi4 = psi4
    # perform initial setup of psi4 python API
    #self.set_psi4(atoms=atoms)


import ase
ase.calculators.calculator.FileIOCalculator.write_input = FileIOCalculator__write_input
ase.calculators.calculator.FileIOCalculator.calculate = FileIOCalculator__calculate
ase.calculators.calculator.FileIOCalculator.acalculate = FileIOCalculator__acalculate
ase.calculators.calculator.Parameters.write = Parameters__write
import ase.calculators.psi4
ase.calculators.psi4.Psi4.__init__ = Psi4__init
