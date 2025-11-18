from pathlib import Path
from cumulus_library_kidney_transplant import fhir2sql

def include(period_start='2008-01-01', period_end='2026-01-01', include_history: bool = True) -> Path:
    """
    :param period_start: patient encounters selected will be >= period_start
    :param period_end: patient encounters selected will be <= period_end
    :param include_history: if True, for patients matching all inclusion criteria, select also all patient history even prior to period_start.
    :return: inclusion criteria for `study_population.py`
    """
    view = fhir2sql.name_join('include', 'study_period')
    cols = ['period_start', 'period_end', 'include_history']
    values = [f"date('{period_start}')",
              f"date('{period_end}')",
              include_history]

    return fhir2sql.criteria2view(view, cols, values)
