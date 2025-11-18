from pathlib import Path

from cumulus_library.builders.counts import CountsBuilder
from cumulus_library_kidney_transplant import filetool, fhir2sql
from cumulus_library_kidney_transplant.filetool import PREFIX

def cube_encounter(source_table='study_population', table_cols=None, table_name=None, min_subject=10) -> Path:
    """
    CUBE counts contain unique numbers of
        * FHIR Encounter --> "select distinct(core__encounter.encounter_ref)"

    :param source_table: line-level cohort to derive counts from
    :param table_cols: columns to include in the CUBE group by expression
    :param table_name: output CUBE table
    :param min_subject: minimum number of subjects to include
    :return: Path to CUBE table
    """
    if not table_name:
        table_name = fhir2sql.name_cube(source_table, 'patient')

    table_cols = sorted(list(set(table_cols)))
    sql = CountsBuilder(PREFIX).count_encounter(
        table_name=table_name,
        source_table=source_table,
        table_cols=table_cols,
        min_subject=min_subject
    )
    sql = as_view(sql, table_name)
    return filetool.save_athena_view(table_name, sql)

def cube_patient(source_table='study_population', table_cols=None, table_name=None, min_subject=10) -> Path:
    """
    CUBE counts contain unique numbers of
        * FHIR Encounter --> "select distinct(core__encounter.encounter_ref)"

    :param source_table: line-level cohort to derive counts from
    :param table_cols: columns to include in the CUBE group by expression
    :param table_name: output CUBE table
    :param min_subject: minimum number of subjects to include
    :return: Path to CUBE table
    """
    if not table_name:
        table_name = fhir2sql.name_cube(source_table, 'patient')

    table_cols = sorted(list(set(table_cols)))
    sql = CountsBuilder(PREFIX).count_patient(
        table_name=table_name,
        source_table=source_table,
        table_cols=table_cols,
        min_subject=min_subject
    )
    sql = as_view(sql, table_name)
    return filetool.save_athena_view(table_name, sql)

def as_view(sql:str, table_name:str) -> str:
    """
    Hackish temp replacement for faster dev lifecycle
    """
    create_table = f'CREATE TABLE {table_name} AS ('
    replace_view = f'CREATE or replace VIEW {table_name} AS '
    return sql.replace(create_table, replace_view).replace(');', ';')

if __name__ == "__main__":
    targets = [

        cube_patient(source_table='irae__gpt4_donor',
                     table_cols=['donor_type_best',
                                 'donor_relationship_best',
                                 'doc_type_display',
                                 'donor_date_best_year',
                                 'donor_hla_quality',
                                 'age_at_visit', 'gender', 'race_display'],
                     table_name=fhir2sql.name_cube('patient_llm_donor')),

        cube_encounter(source_table='irae__gpt4_compliance',
                       table_cols=['rx_compliance_status',
                                   'rx_therapeutic_level',
                                   'rx_therapeutic_sub',
                                   'rx_therapeutic_supra',
                                   'rx_compliance_level',
                                   'rx_compliance_partial',
                                   'rx_compliance_non',
                                   'age_at_visit'],
                       table_name=fhir2sql.name_cube('encounter_llm_compliance')),

        cube_patient(source_table='irae__gpt4_infection',
                     table_cols=['infection_history',
                                 'infection_present',
                                 'confidence', 'present_type', 'present_type_any',
                                 'viral_present',
                                 'bacterial_present',
                                 'fungal_present',
                                 'age_at_visit', 'gender', 'race_display'],
                     table_name=fhir2sql.name_cube('patient_llm_infection')),

        cube_patient(source_table='irae__gpt4_infection_outcome',
                     table_cols=['rx_compliance_status',
                                 'rx_therapeutic_supra',
                                 'infection_type',
                                 'infection_confidence',
                                 'rejection_patient',
                                 'failure_patient'],
                     table_name=fhir2sql.name_cube('patient_infection_outcome')),

        cube_patient(source_table='irae__gpt4_rejection',
                     table_cols=['rejection_encounter',
                                 'rejection_patient',
                                 'failure_present',
                                 'failure_history',
                                 'age_at_visit',
                                 'gender',
                                 'race_display'],
                     table_name=fhir2sql.name_cube('patient_llm_rejection')),
    ]