from typing import List
from pathlib import Path
from cumulus_library_kidney_transplant import (
    manifest,
    filetool,
    criteria,
    study_population,
    cohorts,
    casedef)
from cumulus_library_kidney_transplant.count import cube
from cumulus_library_kidney_transplant.criteria.race import Race
from cumulus_library_kidney_transplant.criteria.encounter_class import EncounterClass
from cumulus_library_kidney_transplant.variable import (
    aspect,
    vsac_variables,
    vsac_markdown,
    loinc_doc,
    custom_variables)

###############################################################################
#
# Config(...)
#
###############################################################################

class StudyBuilderConfig:
    """
    IRAE inclusion criteria builder config.
    inclusion/exclusion criteria specifies which patient encounters to build.

    Attributes:
        period_start (str): First FHIR Encounter.actualPeriod, in YYYY-MM-DD format.
        period_end (str): Latest FHIR Encounter.actualPeriod, in YYYY-MM-DD format.
        include_history (bool): Include patient history before period_start if other criteria is met.
        enc_class_list (list): FHIR Encounter.cass
        enc_min (int): Minimum number of FHIR encounters per patient.
        enc_max (int): Maximum number of FHIR encounters per patient.
        enc_days_min (int): Minimum days from first to latest FHIR encounter.
        enc_days_max (int): Maximum days from first to latest FHIR encounter.
        age_min (int): Minimum FHIR patient calculated age_at_visit.
        age_max (int): Maximum FHIR patient calculated age_at_visit.
        gender_female (bool): Include FHIR patient.gender=female.
        gender_male (bool): Include FHIR patient.gender=male.
        gender_other (bool): Include FHIR patient.gender=other.
        gender_unknown (bool): Include FHIR patient.gender=unknown.
        race_list (List[Race] | List[str]): Include FHIR patient.race
        aspect_map (aspect.AspectMap | dict): build AspectKey {
                        vsac_variables_defined methods:
                        "labs" : .get_labs()
                        "medications", .get_medications()
                        "diagnoses", .get_diagnoses()
                        "document", .get_documents()
                        "procedure" .get_procedures()}
    """
    period_start: str = '2008-01-01'
    period_end: str = '2026-02-01'
    include_history: bool = True
    enc_class_list: List[EncounterClass] | List[str] = None
    enc_min: int = 3
    enc_max: int = 1000
    enc_days_min: int = 90
    enc_days_max: int = 36500
    age_min: int = 0
    age_max: int = 120
    gender_female: bool = True
    gender_male: bool = True
    gender_other: bool = True
    gender_unknown: bool = True
    race_list: List[Race] | List[str] = None
    aspect_map: aspect.AspectMap | dict = None

    def __init__(self, form: dict = None):
        """
        :param form: optionally override default study builder configuration.
        """
        if not form:
            form = dict()
        self.period_start = form.get('period_start', '2008-01-01')
        self.period_end = form.get('period_end', '2026-01-01')
        self.include_history = bool(form.get('include_history', True))
        self.enc_class_list = form.get('enc_class_list', None)
        self.enc_min = int(form.get('enc_min', 3))
        self.enc_max = int(form.get('enc_max', 1000))
        self.enc_days_min = int(form.get('days_min', 90))
        self.enc_days_max = int(form.get('days_max', 365000))
        self.age_min = int(form.get('age_min', 0))
        self.age_max = int(form.get('age_max', 120))
        self.gender_female = bool(form.get('gender_female', True))
        self.gender_male = bool(form.get('gender_male', True))
        self.gender_other = bool(form.get('gender_other', True))
        self.gender_unknown = bool(form.get('gender_unknown', True))
        self.race_list = form.get('race_list', None)
        self.aspect_map = form.get('aspect_map', None)

    def as_json(self) -> dict:
        return self.__dict__

    @staticmethod
    def read_config(from_path: str | Path = None) -> dict:
        """
        :param from_path:  StudyBuilderConfig.json default
        :return: dict JSON of StudyBuilderConfig
        """
        if not from_path:
            from_path = filetool.path_home('StudyBuilderConfig.json')
        return filetool.read_json(from_path)

    @staticmethod
    def make_config(from_path: str | Path = None):
        """
        :param from_path: StudyBuilderConfig.json default
        :return: StudyBuilderConfig parsed object
        """
        return StudyBuilderConfig(StudyBuilderConfig.read_config(from_path))

###############################################################################
#
# Make
#
###############################################################################
def make_study_sql(study: StudyBuilderConfig = None) -> List[Path]:
    """
    Command line invocation of the study builder is done using Cumulus Library:
    https://docs.smarthealthit.org/cumulus/library/

    $cumulus-library build -s ./ -t irae

    :return: list of SQL files to execute in Athena.
    """
    if study is None:
        print('loading default path for study builder configuration')
        study = StudyBuilderConfig.make_config()

    criteria_sql = [
        # Study Period
        criteria.study_period.include(
            period_start=study.period_start,
            period_end=study.period_end,
            include_history=study.include_history
        ),
        # FHIR Encounter Health Care Utilization Criteria
        criteria.utilization.include(
            enc_min=study.enc_min,
            enc_max=study.enc_max,
            days_min=study.enc_days_min,
            days_max=study.enc_days_max
        ),
        # Age at visit criteria, default ANY
        # Calculated from FHIR Patient.birthDate (age_at_visit)
        # https://www.hl7.org/fhir/patient-definitions.html#Patient.birthDate
        criteria.age_at_visit.include(
            age_min=study.age_min,
            age_max=study.age_max
        ),
        # FHIR Encounter.cass criteria, default ANY.
        # https://terminology.hl7.org/6.2.0/ValueSet-v3-ActEncounterCode.html
        criteria.encounter_class.include(
            enc_class_list=study.enc_class_list
        ),
        # FHIR Patient.gender, default ANY
        criteria.gender.include(
            female=study.gender_female,
            male=study.gender_male,
            other=study.gender_other,
            unknown=study.gender_unknown
        ),
        # FHIR Patient.race, default ANY
        criteria.race.include(
            race_list=study.race_list)]

    return (criteria_sql +
            study_population.make() +
            loinc_doc.make() +
            vsac_variables.make() +
            custom_variables.make() +
            cohorts.make() +
            casedef.make() +
            cube.make())


def make_study(study: StudyBuilderConfig= None) -> Path:
    sql_files = make_study_sql(study)
    vsac_markdown.make()
    return manifest.write_manifest(sql_files)

if __name__ == "__main__":
    make_study()
