from pathlib import Path
from typing import List
from cumulus_library_kidney_transplant import fhir2sql, filetool

########################################################################################################
# CASE DEFINITION
##########################################################################################################
def name_casedef() -> str:
    """
    :return: str Tablename of casedef like irae__cohort_casedef
    """
    return fhir2sql.name_join('cohort', 'casedef')

def make_casedef_custom_csv() -> Path:
    """
    Load the custom case definition CSV file.
    """
    file_csv = filetool.path_spreadsheet('casedef_custom.csv')
    view_name_csv = fhir2sql.name_prefix('casedef_custom_csv')
    return fhir2sql.csv2view(file_csv, view_name_csv)

def make_casedef_custom() -> Path:
    """
    Flag Include/Exclude rules for "First" encounters.
    """
    file_sql = filetool.load_template('casedef.sql')
    view_name = fhir2sql.name_prefix('casedef')
    return fhir2sql.save_athena_view(view_name, file_sql)

########################################################################################################
# Select cohorts matching casedef
##########################################################################################################
def make_cohort(include_exclude: str = None) -> Path:
    """
    :param include_exclude: name of the SQL Template to make the cohort from
    :return: Path to cohort_casedef SQL
    """
    if include_exclude is None:
        table = name_casedef()
    else:
        table = f"{name_casedef()}_{include_exclude}"
    sql = filetool.load_template(f'{table}.sql')
    return filetool.save_athena_view(table, sql)

########################################################################################################
# Index first encounter matching case definition
##########################################################################################################

def make_index_date(cohort_table, period, equality) -> Path:
    """
    Index date refers when the case definition criteria was first met.
    This means the first Encounter where $variable was recorded for each patient.

    `template/cohort_casedef_index.sql`

    :param cohort_table: case definition variable table
    :param period:
        "pre"= select cohort BEFORE case definition first encounter;
        "index" = select cohort DURING case definition first encounter;
        "post"= select cohort AFTER case definition first encounter
    :param equality: date comparison "=", "<", ">"
    :return: Path to SQL table containing cohort matching case definition
    """
    template = 'cohort_casedef_period.sql'
    view = f'{name_casedef()}_{period}.sql'
    sql = filetool.load_template(template)
    sql = sql.replace('$period', period)
    sql = sql.replace('$equality', equality)
    return filetool.save_athena(view, sql)

########################################################################################################
# Timeline (pre/index/post) view with `cohort_casedef`
##########################################################################################################

def make_timeline() -> Path:
    """
    Return a timeline of the case definition with respect to all study variables.
    see `template/cohort_casedef_timeline.sql`
    :return: SQL file of case definition cohort as a timeline sequence of events.
    """
    template = fhir2sql.name_join('cohort', 'casedef_timeline') + '.sql'
    sql = filetool.load_template(template)
    sql = filetool.inline_template(sql)
    return filetool.save_athena(template, sql)

########################################################################################################
# Samples for Chart Review and QA
##########################################################################################################
def make_samples(size: int = None, period: str = 'post') -> Path:
    """
    This method is for sampling Documents for LLM/ChartReview.
    This is not used to generate CUBE data.

    See `template/sample_casedef*`

    :param size: number of FHIR DocumentReference samples to select from casedef
    :param period: "pre", "index", or "post", samples from before, during, or after first casedef encounter.
    :return: Path to SQL file with case definition samples.
    """
    table = fhir2sql.name_sample('casedef')
    if size:
        template = f"{table}_size.sql"
        target = f"{table}_{period}_{size}.sql"
    else:
        template = f"{table}.sql"
        target = f"{table}_{period}.sql"

    sql = filetool.load_template(template)
    sql = filetool.inline_template(sql)
    sql = sql.replace('$size', str(size))
    sql = sql.replace('$period', period)
    return filetool.save_athena(target, sql)


def make() -> List[Path]:
    """
    Case Definition processing steps
    1. Load custom CSV file containing metatadata into Athena SQL

    2. Process SQL table with include/exclude rules.

    3. Create cohort of patients matching case definition

    4. "Exclude" (flag) patients matching the case definition for whome exclusion criteria was found.
    For example, patients who had a transplant *outcome* before a kidney transplant diagnosis or surgery.

    5. "Include" (flag) patients matching the case definition for whome exclusion criteria was found.
    The include cohort is the set of patients MINUS the exclude patients from previous step.

    6. CTAS "Index": first encounter matching the case definition.
    This is the "index date" (medical research term not SQL index).

    7. CTAS "Pre" encounters before index date for patients matching the case definition.
    This is the patient longitudinal history.

    8. CTAS "Post" encounters after index date for patients matching the case definition.
    This is the patient treatment and outcome cohort.

    9. "Timeline" is a simple unified view of pre/index/post tables with a column designating "period".

    10. "samples" of documented encounters are selected at varying sizes for each "period" .
    * "index"   samples (All, 10 patients, and 100 patients)
    * "pre"     samples (All, 10 patients, and 100 patients)
    * "post"    samples (All, 10 patients, and 100 patients)

    :return: List of SQL table cohorts selected before and after the case definition +timeline +samples
    """
    cohort_table = fhir2sql.name_join('cohort', 'casedef')

    return [make_casedef_custom_csv(),
            make_casedef_custom(),
            make_cohort(),
            make_cohort('exclude'),
            make_cohort('include'),
            make_index_date(cohort_table, 'index', '='),
            make_index_date(cohort_table, 'pre', '<'),
            make_index_date(cohort_table, 'post', '>'),
            make_timeline(),
            make_samples(None, 'index'),
            make_samples(10, 'index'),
            make_samples(100, 'index'),
            make_samples(None, 'pre'),
            make_samples(10, 'pre'),
            make_samples(100, 'pre'),
            make_samples(None, 'post'),
            make_samples(10, 'post'),
            make_samples(100, 'post')]
