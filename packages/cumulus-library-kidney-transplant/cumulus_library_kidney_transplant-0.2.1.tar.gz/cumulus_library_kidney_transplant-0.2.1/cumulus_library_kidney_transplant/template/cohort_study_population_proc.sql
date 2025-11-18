create table $prefix__cohort_study_population_proc as
select distinct
    PROC.status                     as proc_status,
    PROC.code_code                  as proc_code,
    PROC.code_display               as proc_display,
    PROC.code_system                as proc_system,
    PROC.performeddatetime_day      as proc_performed_day,
    PROC.performeddatetime_month    as proc_performed_month,
    PROC.performeddatetime_year     as proc_performed_year,
    PROC.procedure_ref,
    study_population.*
from
    $prefix__cohort_study_population as study_population,
    core__procedure as PROC
where
    study_population.encounter_ref = PROC.encounter_ref
;
