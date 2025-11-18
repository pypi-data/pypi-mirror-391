from enum import Enum
from typing import List
from pathlib import Path
from cumulus_library_kidney_transplant.variable import vsac_variables, custom_variables
from cumulus_library_kidney_transplant import fhir2sql, filetool

class VariableMulti:
    dx: str = None
    rx: str = None
    lab: str = None
    proc: str = None
    doc: str = None

    def __init__(self, dx: str = None, rx: str = None, lab: str = None, proc: str = None, doc: str = None):
        self.dx = dx
        self.rx = rx
        self.lab = lab
        self.proc = proc
        self.doc = doc

###############################################################################
# VSAC and custom variables list
###############################################################################
def list_variables() -> List[str]:
    return list(sorted(vsac_variables.list_view_variables()) + list(sorted(custom_variables.list_view_custom())))

def make_diabetes() -> List[Path]:
    text = filetool.load_template('cohort_multi_variable.sql')
    text = filetool.inline_template(text, 'diabetes')
    file = filetool.path_athena(fhir2sql.name_cohort('multi_diabetes.sql'))
    return [filetool.save_athena(file, text)]

###############################################################################
# VSAC and custom variables list
###############################################################################
def make() -> List[Path]:
    return make_diabetes()


if __name__ == "__main__":
    print(make())
