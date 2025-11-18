create table $prefix__cohort_study_variables as
with variable_cohorts as
(
$variable_list
)
select distinct
    variable_cohorts.variable,
    variable_cohorts.valueset,
    variable_cohorts.code,
    variable_cohorts.display,
    variable_cohorts.system,
    SP.status,
    SP.age_at_visit,
    SP.gender,
    SP.race_display,
    SP.ethnicity_display,
    SP.enc_class_code,
    SP.enc_period_start_day,
    SP.enc_period_start_month,
    SP.enc_period_start_year,
    SP.enc_period_end_day,
    SP.encounter_ref,
    SP.subject_ref
from
    variable_cohorts,
    $prefix__cohort_study_population as SP
where
    variable_cohorts.encounter_ref = SP.encounter_ref
;

