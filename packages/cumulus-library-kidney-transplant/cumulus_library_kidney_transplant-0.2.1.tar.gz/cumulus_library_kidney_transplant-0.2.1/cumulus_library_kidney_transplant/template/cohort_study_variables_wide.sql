create table $prefix__cohort_study_variables_wide as
with lookup as
(
    select  distinct variable, valueset, encounter_ref
    from    $prefix__cohort_study_variables
)
select distinct
    lookup.variable,
    $variable_list,
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
from $prefix__cohort_study_population as SP
left join lookup on SP.encounter_ref = lookup.encounter_ref
