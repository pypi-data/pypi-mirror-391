from enum import Enum
from pathlib import Path
from cumulus_library_kidney_transplant import guard, fhir2sql

class ObservationCategory(Enum):

    social_history = ('social-history', 'Occupational, lifestyle, social, familial, environmental, health risk factors')
    vital_signs = ('vital-signs', 'Vital Signs: BP, HR, RR, height, weight, BMI, head circumference, O2SAT, Temp')
    imaging = ('imaging', 'x-ray, ultrasound, CT, MRI, angiography, echocardiography, and nuclear medicine')
    laboratory = ('laboratory', 'chem, heme, serology, histology, cytology, pathology, microbiology, virology')
    procedure = ('procedure', 'interventional and non-interventional procedures')
    survey = ('survey', 'assessment tool/survey instrument observations')
    exam = ('exam', 'physical exam findings')
    therapy = ('therapy', 'occupational, physical, radiation, nutritional and medication therapy')
    activity = ('activity', 'bodily activity that enhances or maintains physical fitness')

    def __init__(self, code, display):
        self.system = 'http://terminology.hl7.org/CodeSystem/observation-category'
        self.code = code
        self.display = display


def include(category_list=None) -> Path:
    """
    Selected Encounter observations specified by "category_list" to compile the `study_population`
    :param category_list: 1+ observation category types, either as ObservationCategory(Enum) or FHIR Coding.
    :return: SQL inclusion criteria to select study population
    """
    if not category_list:
        category_list = list(ObservationCategory)
    codes = guard.as_list_coding(category_list)
    return fhir2sql.include(codes, 'enc_class')
