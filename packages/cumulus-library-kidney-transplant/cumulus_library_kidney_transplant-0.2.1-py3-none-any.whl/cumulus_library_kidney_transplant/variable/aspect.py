from enum import Enum
from typing import List, Dict
from cumulus_library_kidney_transplant import guard

class Valueset:
    def __init__(self, name: str, oid: List[str] | str | None):
        self.name = name
        self.oid = oid

    def as_json(self):
        return {self.name: self.oid}

class Variable:
    def __init__(self, name: str, valuesets: List[Valueset] | Dict[str, str] | Dict[str, list]):
        self.name = name.lower()
        self.valueset_list = list()
        if valuesets:
            if guard.is_list_type(valuesets, Valueset):
                self.valueset_list = valuesets
            elif guard.is_dict(valuesets):
                self.valueset_list = list()
                for vs_name in valuesets.keys():
                    vs_name = vs_name.lower()
                    self.valueset_list.append(Valueset(vs_name, valuesets.get(vs_name)))

    def as_json(self) -> dict:
        return {self.name: [vs.as_json() for vs in self.valueset_list]}

class AspectKey(Enum):
    dx = 'diagnoses'
    rx = 'medications'
    lab = 'labs'
    proc = 'procedures'
    doc = 'document'
    diag = 'diagnostic_report'

    def as_json(self):
        return {self.name: self.value}

    @staticmethod
    def list_keys() -> list[str]:
        return [key.name for key in AspectKey]

class Aspect:
    variable_list = List[Variable]
    key = AspectKey

    def __init__(self, variable_list: List[Variable] | Dict[str, Dict[str, str]]):
        self.variable_list = list()

        if guard.is_list_type(variable_list, Variable):
            self.variable_list = variable_list

        elif guard.is_dict(variable_list):
            for var_name in variable_list.keys():
                vs_list = [Valueset(key, val) for key, val in variable_list.get(var_name).items()]
                self.variable_list.append(Variable(var_name, vs_list))
        self._guard_var_key()

    def _guard_var_key(self):
        """
        Guard Variable Key name to ensure using the AspectKey prefix
        """
        guard_list = list()
        for var in self.variable_list:
            var.name = var.name.lower()
            if not var.name.startswith(self.key.name):
                var.name = f'{self.key.name}_{var.name}'
            guard_list.append(var)
        self.variable_list = guard_list

    def as_json(self) -> dict:
        return {self.key.name: [v.as_json() for v in self.variable_list]}

class Diagnoses(Aspect):
    key = AspectKey.dx

class Medications(Aspect):
    key = AspectKey.rx

class Labs(Aspect):
    key = AspectKey.lab

class Procedures(Aspect):
    key = AspectKey.proc

class Documents(Aspect):
    key = AspectKey.doc

class AspectMap:
    def __init__(self,
                 diagnoses: Diagnoses | None,
                 medications: Medications | None,
                 labs: Labs | None,
                 procedures: Procedures | None,
                 documents: Documents | None):
        self.diagnosis = diagnoses
        self.medications = medications
        self.labs = labs
        self.procedures = procedures
        self.documents = documents

    def as_list(self) -> List[Aspect]:
        return [self.diagnosis, self.medications, self.labs, self.procedures, self.documents]

    def as_json(self) -> dict:
        return self.diagnosis.as_json() | \
               self.medications.as_json() | \
               self.labs.as_json() | \
               self.procedures.as_json() | \
               self.documents.as_json()
