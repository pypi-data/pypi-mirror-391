from pathlib import Path
from cumulus_library_kidney_transplant import fhir2sql

def include(enc_min=0, enc_max=1000, days_min=0, days_max=36500) -> Path:
    """
    :param enc_min: Min count of encounters during `study_period`
    :param enc_max: Max count of encounters during `study_period`
    :param days_min: Min days between first and last encounter in the `study_period`
    :param days_max: Max days between first and last encounter in the `study_period`
    :return: inclusion criteria for `study_population`
    """
    view = fhir2sql.name_join('include', 'utilization')
    cols = ['enc_min', 'enc_max', 'days_min', 'days_max']
    values = [enc_min, enc_max, days_min, days_max]
    return fhir2sql.criteria2view(view, cols, values)
