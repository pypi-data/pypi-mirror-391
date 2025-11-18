from typing import List
from pathlib import Path
from fhirclient.models.coding import Coding
from cumulus_library_kidney_transplant import guard, fhir2sql, filetool

FILE_JSON = 'valueset-vsac-encounter-types.json'

def get_valueset(filename=FILE_JSON) -> dict:
    return filetool.load_valueset(filename)

def list_coding(filename=FILE_JSON) -> List[Coding]:
    return fhir2sql.expansion2codelist(str(filename))

def include(code_list: List[str] = None) -> Path:
    """
    Selected encounters specified by "enc_class_list" to compile the `study_population`
    :param enc_type_list: 1+ encounter class types, either as EncounterClass(Enum) or FHIR Coding.
    :return: SQL inclusion criteria to select study population
    """
    standard = list_coding()
    if not code_list:
        code_list = standard
    code_list = guard.filter_list_coding(standard, code_list)
    return fhir2sql.include(code_list, 'enc_class')
