from enum import Enum
from pathlib import Path
from cumulus_library_kidney_transplant import fhir2sql, guard

class Gender(Enum):
    """
    http://hl7.org/fhir/codesystem-gender-identity.html
    http://hl7.org/fhir/patient.html#gender
    http://hl7.org/fhir/valueset-administrative-gender.html
    """
    male = 'male'
    female = 'female'
    trans_female = 'transgender-female'
    trans_male = 'transgender-male'
    non_binary = 'non-binary'
    non_disclose = 'non-disclose'
    other = 'other'
    unknown = 'unknown'

    def __init__(self, code=None):
        self.system = 'http://hl7.org/fhir/ValueSet/administrative-gender'
        self.code = code
        self.display = code

def include(female=True, male=True, other=True, unknown=True) -> Path:
    """
    :param female: Patient.gender
    :param male: Patient.gender
    :param other: Patient.gender
    :param unknown: Patient.gender
    :return: SQL inclusion criteria to select study population
    """
    codes = list()

    if female:
        codes.append(Gender.female)
    if male:
        codes.append(Gender.male)
    if other:
        codes.append(Gender.other)
    if unknown:
        codes.append(Gender.unknown)

    codes = [guard.as_coding(c) for c in codes]

    return fhir2sql.include(codes, 'gender')
