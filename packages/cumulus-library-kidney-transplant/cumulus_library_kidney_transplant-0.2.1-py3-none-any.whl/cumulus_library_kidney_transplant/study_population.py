from typing import List
from pathlib import Path
from cumulus_library_kidney_transplant import fhir2sql
from cumulus_library_kidney_transplant import filetool

def list_tables() -> List[str]:
    """
    :return: list of tables in the `study_population`, one for each AspectKey
    """
    table = fhir2sql.name_join('cohort', 'study_population')
    return [table] + fhir2sql.list_table_aspect(table)

# MHG: The following two functions don't actually create files
def make_meta_date() -> List[Path]:
    """
    :return:
    """
    table = fhir2sql.name_prefix('meta_date')
    sql = filetool.load_template(f'meta_date.sql')
    return [filetool.save_athena_view(table, sql)]

def make_meta_version() -> List[Path]:
    """
    :return:
    """
    table = fhir2sql.name_prefix('meta_version')
    sql = filetool.load_template(f'meta_version.sql')
    return [filetool.save_athena_view(table, sql)]

def make_study_period() -> List[Path]:
    return [filetool.copy_template('cohort_study_period.sql')]

def make_study_population() -> List[Path]:
    """
    Study Population is built from "template/" dir.
    Study Population matches inclusion/exlusion criteria from `StudyBuilderConfig`.
    Study Population contains all Patient encounters matching criteria and all FHIR resources below.

    Study Builder then builds each `AspectKey`:
        dx = 'diagnoses'
        rx = 'medications'
        lab = 'labs'
        proc = 'procedures'
        doc = 'document'
        diag = 'diagnostic_report'

    Produces:
    * cohort_study_population.sql       Patient Encounters matching criteria
    * cohort_study_population_dx.sql    -> FHIR Condition
    * cohort_study_population_rx.sql    -> FHIR MedicationRequest
    * cohort_study_population_lab.sql   -> FHIR Observation.category=lab
    * cohort_study_population_doc.sql   -> FHIR DocumentReference
    * cohort_study_population_proc.sql  -> FHIR Procedure
    * cohort_study_population_diag.sql  -> FHIR DiagnosticReport

    :return: list of SQL `study_population`
    """
    file_list = list()
    for table in list_tables():
        sql = filetool.load_template(f'{table}.sql')
        sql = filetool.inline_template(sql)
        file_list.append(filetool.save_athena_view(table, sql))
    return file_list

def make() -> List[Path]:
    return make_study_period() + make_study_population() + make_meta_date() + make_meta_version()
