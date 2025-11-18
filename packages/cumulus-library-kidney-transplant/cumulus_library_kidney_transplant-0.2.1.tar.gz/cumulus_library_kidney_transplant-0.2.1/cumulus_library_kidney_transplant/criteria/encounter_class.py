from enum import Enum
from typing import List
from pathlib import Path
from cumulus_library_kidney_transplant import fhir2sql, guard

class EncounterClass(Enum):
    AMB = ('AMB', 'ambulatory')
    EMER = ('EMER', 'emergency')
    FLD = ('FLD', 'field')
    HH = ('HH', 'home health')
    IMP = ('IMP', 'inpatient encounter')
    ACUTE = ('ACUTE', 'inpatient acute')
    NONAC = ('NONAC', 'inpatient non-acute')
    OBSENC = ('OBSENC', 'observation encounter')
    PRENC = ('PRENC', 'pre-admission')
    SS = ('SS', 'short stay')
    VR = ('VR', 'virtual')

    def __init__(self, code, display=None):
        """
        https://terminology.hl7.org/1.0.0//ValueSet-v3-ActEncounterCode.html
        :param code: encounter code
        :param display: display label
        """
        self.system = 'http://terminology.hl7.org/ValueSet/v3-ActEncounterCode'
        self.code = code
        self.display = display

def include(enc_class_list: List[EncounterClass] | List[str] = None) -> Path:
    """
    Selected encounters specified by "enc_class_list" to compile the `study_population`
    :param enc_class_list: 1+ encounter class types, either as EncounterClass(Enum) or FHIR Coding.
    :return: SQL inclusion criteria to select study population
    """
    if not enc_class_list:
        enc_class_list = list(EncounterClass)

    if guard.is_list_type(enc_class_list, EncounterClass):
        enc_class_list = guard.as_list_coding(enc_class_list)

    codes = guard.filter_list_coding(list(EncounterClass), enc_class_list)
    return fhir2sql.include(codes, 'enc_class')
