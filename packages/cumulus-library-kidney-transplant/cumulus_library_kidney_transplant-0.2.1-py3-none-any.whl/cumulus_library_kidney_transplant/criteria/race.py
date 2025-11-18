from enum import Enum
from typing import List
from pathlib import Path
from fhirclient.models.coding import Coding
from cumulus_library_kidney_transplant import guard, fhir2sql

class Race(Enum):
    """
    Race coding has 5 "path_home" levels, called the R5 shown below.
    http://hl7.org/fhir/r4/v3/Race/cs.html
    """
    asian = ('2028-9', 'Asian')
    black = ('2054-5', 'Black or African American')
    native_american_or_alaskan = ('1002-5', 'American Indian or Alaska Native')
    native_hawaiian_pacific_islander = ('2076-8', 'Native Hawaiian or Other Pacific Islander')
    white = ('2106-3', 'White')

    def __init__(self, code, display=None):
        self.system = 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-race'
        self.code = code
        self.display = display

    @staticmethod
    def lookup(race_list: List[str]) -> List:
        """
        TODO: refactor DRY
        Get EncounterClass by "code" list in `enc_class_list`
        :param race_list: list of str "codes" to return into EncounterClass types.
        :return: List[EncounterClass] entries for the "codes" in `enc_class_list`
        """
        race_list = [code.upper() for code in race_list]
        results = list()
        for standard in list(Race):
            if standard.name in race_list:
                results.append(standard)
        return results

def include(race_list=None | Race | List[Race] | List[Coding]) -> Path:
    """
    :param race_list: List of CDC High Level race groups
    :return: inclusion criteria for `study_population`
    """
    if not race_list:
        race_list = list(Race)
    codes = guard.as_list_coding(race_list)
    return fhir2sql.include(codes, 'race')
