from enum import Enum

class VitalSign(Enum):
    """
    @see also https://hl7.org/fhir/observation-vitalsigns.html
    """
    panel = ('85353-1', 'Vital Signs Panel')
    rr_respiratory_rate = ('9279-1', 'Respiratory Rate')
    hr_heart_rate = ('8867-4', 'Heart Rate (')
    oxygen_sat = ('2708-6', 'Oxygen saturation in Arterial blood (example: pulse oximetry)')
    temperature = ('8310-5', 'Body Temperature')
    height = ('8302-2', 'Body Height')
    weight = ('29463-7', 'Body weight')
    bmi = ('39156-5', 'Body Mass Index')
    bp = ('85354-9', 'blood pressure systolic and/or diastolic')
    bp_systolic = ('8480-6', 'Systolic blood pressure')
    bp_diastolic = ('8462-4', 'Diastolic blood pressure')
    circumference = ('9843-4', 'head circumference')

    def __init__(self, code, display=None):
        self.system = 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-vital-signs'
        self.code = code
        self.display = display
