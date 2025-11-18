from typing import List
from pathlib import Path
from cumulus_library.builders.counts import CountsBuilder
from cumulus_library_kidney_transplant import filetool, fhir2sql
from cumulus_library_kidney_transplant.variable import vsac_variables, custom_variables
from cumulus_library_kidney_transplant.count.columns import Columns, Duration
from cumulus_library_kidney_transplant import manifest

def get_counts_builder() -> CountsBuilder:
    return CountsBuilder(study_prefix=None, manifest=manifest.get_study_manifest())

def name_cohort(from_table=None) -> str:
    if 'sample' in from_table:
        return from_table
    if 'cohort' in from_table:
        return from_table
    else:
        return fhir2sql.name_cohort(from_table)

def cube_enc(from_table='study_population', cols=None, cube_table=None) -> Path:
    """
    CUBE counts contain unique numbers of
        * FHIR Encounter --> "select distinct(core__encounter.encounter_ref)"

    :param from_table: line-level cohort to derive counts from
    :param cols: columns to include in the CUBE group by expression
    :param cube_table: output CUBE table
    :return: Path to CUBE table
    """
    from_table = name_cohort(from_table)

    if not cube_table:
        cube_table = fhir2sql.name_cube(from_table, 'encounter')

    if not cols:
        cols = Columns.cohort.value + Columns.demographics.value

    cols = sorted(list(set(cols)))
    sql = get_counts_builder().count_encounter(cube_table, from_table, cols)
    return filetool.save_athena_view(cube_table, sql)

def cube_pat(from_table='study_population', cols=None, cube_table=None) -> Path:
    """
    CUBE counts contain unique numbers of
        * FHIR Patient --> "select distinct(core__patient.subject_ref)"

    :param from_table: line-level cohort to derive counts from
    :param cols: columns to include in the CUBE group by expression
    :param cube_table: output CUBE table
    :return: Path to CUBE table
    """
    from_table = name_cohort(from_table)

    if not cube_table:
        cube_table = fhir2sql.name_cube(from_table, 'patient')

    if not cols:
        cols = Columns.cohort.value + Columns.demographics.value

    cols = sorted(list(set(cols)))
    sql = get_counts_builder().count_patient(cube_table, from_table, cols)
    return filetool.save_athena_view(cube_table, sql)

def cube_doc(from_table='study_population', cols=None, cube_table=None) -> Path:
    """
    CUBE counts contain unique numbers of
        * FHIR DocumentReference --> "select distinct(core__documentreference.documentreference_ref)"

    :param from_table: line-level cohort to derive counts from
    :param cols: columns to include in the CUBE group by expression
    :param cube_table: output CUBE table
    :return: Path to CUBE table
    """
    from_table = name_cohort(from_table)

    if not cube_table:
        cube_table = fhir2sql.name_cube(from_table, 'document')

    if not cols:
        cols = Columns.cohort.value + Columns.demographics.value

    cols = sorted(list(set(cols)))
    sql = get_counts_builder().count_documentreference(cube_table, from_table, cols, skip_status_filter=True)
    return filetool.save_athena_view(cube_table, sql)

def make_study_population() -> List[Path]:
    """
    CUBE each study population cohort by unique
    * FHIR Patient
    * FHIR Encounter

    :return: List of SQL files in athena
        * irae__cohort_study_population
        * irae__cohort_study_population_dx
        * irae__cohort_study_population_rx
        * irae__cohort_study_population_lab
        * irae__cohort_study_population_proc
        * irae__cohort_study_population_doc
    """
    return [
            cube_pat(),
            cube_enc(),
            cube_pat('study_population_dx', Columns.cohort.value + Columns.diagnoses.value),
            cube_enc('study_population_dx', Columns.cohort.value + Columns.diagnoses.value),
            cube_pat('study_population_rx', Columns.cohort.value + Columns.medications.value),
            cube_enc('study_population_rx', Columns.cohort.value + Columns.medications.value),
            cube_pat('study_population_lab', Columns.cohort.value + Columns.labs.value),
            cube_enc('study_population_lab', Columns.cohort.value + Columns.labs.value),
            cube_pat('study_population_doc', Columns.cohort.value + Columns.documents.value),
            cube_doc('study_population_doc', Columns.cohort.value + Columns.documents.value),
            cube_pat('study_population_proc', Columns.cohort.value + Columns.procedures.value),
            cube_enc('study_population_proc', Columns.cohort.value + Columns.procedures.value)]

def make_study_population_duration(duration: Duration | str) -> Path:
    """
    CUBE study population by a time duration
    :param duration: week, month, or year
    :return: path to SQL counts file
    """
    if isinstance(duration, Duration):
        duration = duration.value

    return cube_enc(from_table='study_population',
                    cols=(Columns.cohort.value + Columns.month.value),
                    cube_table=fhir2sql.name_cube(f'encounter_study_population_{duration}'))

def make_variables() -> List[Path]:
    """
    CUBE each study variable cohort by unique FHIR Patient.
    See `columns.py` for columns included in the CUBE group by expression.

    Variables includes both
    * `vsac_variables.py`
    * `custom_variables.py`

    :return: List of study variable CUBE tables
    """
    source = fhir2sql.name_cohort('study_variables')
    cols = Columns.valueset.value + ['variable']
    file_list = [cube_pat(source, cols),
                 cube_enc(source, cols)]

    variable_list = vsac_variables.list_view_variables() + custom_variables.list_view_custom()
    for variable in variable_list:
        if '__dx' in variable:
            file_list.append(cube_pat(variable, Columns.valueset.value + Columns.diagnoses.value))
        elif '__rx' in variable:
            file_list.append(cube_pat(variable, Columns.valueset.value + Columns.medications.value))
        elif '__lab' in variable:
            file_list.append(cube_pat(variable, Columns.valueset.value + Columns.labs.value))
        elif '__proc' in variable:
            file_list.append(cube_pat(variable, Columns.valueset.value + Columns.procedures.value))
        elif '__doc' in variable:
            file_list.append(cube_pat(variable, Columns.valueset.value + Columns.documents.value))
    return file_list

def make_casedef_timeline() -> List[Path]:
    """
    CUBE count casedef_timeline using columns
        * period (sequence of events) pre/index/after the case definition index date
        * variable
        * valueset
        * FHIR Encounter (calculated month)

    CUBE counts contain unique numbers of
        * FHIR Patient
        * FHIR Encounter

    :return: Path to CUBE table for the casedef_timeline
    """
    from_table = fhir2sql.name_cohort('casedef_timeline')
    cols = ['casedef_period', 'age_at_visit', 'gender', 'enc_period_start_year']
    return [cube_pat(from_table, cols),
            cube_enc(from_table, cols)]

def make_casedef_samples() -> List[Path]:
    """
    CUBE count casedef_timeline using columns
        * period (sequence of events) pre/index/after the case definition index date
        * variable
        * valueset
        * FHIR Encounter (calculated month)

    FYI this method depends on issue #53, requires FHIR Encounter.status column to be present.
    https://github.com/smart-on-fhir/cumulus-library-kidney-transplant/issues/53

    CUBE counts contain unique numbers of
        * FHIR Patient
        * FHIR Encounter

    :return: Path to CUBE table for the casedef_timeline
    """
    cols = ['doc_type_code', 'doc_type_display', 'doc_type_system', 'group_name']
    file_list = list()
    for period in ['pre', 'index', 'post']:
        for size in [None, '10', '100']:
            if size:
                from_table = fhir2sql.name_sample(f'casedef_{period}_{size}')
                file_list.append(cube_doc(from_table, cols))
            else:
                from_table = fhir2sql.name_sample(f'casedef_{period}')
                file_list.append(cube_pat(from_table, cols))
                file_list.append(cube_doc(from_table, cols))
    return file_list

def make() -> List[Path]:
    """
    Make CUBE "powerset" tables using Athena (Trino Cube function)
    https://trino.io/docs/current/sql/select.html#cube

    CUBE counts contain unique numbers of
        * FHIR Patient
        * FHIR Encounter

    CUBE tables are generated with the format
        * irae__count_[patient|encounter]_$cohort

    CUBE tables are created from COHORTS
        * cohort_study_population
        * cohort_study_population_dx
        * cohort_study_population_rx
        * cohort_study_population_lab
        * cohort_study_population_proc
        * cohort_study_population_doc
        * cohort_casedef_timeline

    CUBE data are generate for each
        * cohort_$variable

    :return: List of SQL files for each CUBE output
    """
    return (make_study_population() +
            make_variables() +
            make_casedef_timeline() +
            make_casedef_samples())
