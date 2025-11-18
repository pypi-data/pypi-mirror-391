create table $prefix__cohort_study_population_dx as
select distinct
    DX.category_code    as dx_category_code,
    DX.code             as dx_code,
    replace(DX.code_display, chr(10), ' ') as dx_display,
    DX.system           as dx_system,
    DX.condition_ref    as condition_ref,
    study_population.*
from
    $prefix__cohort_study_population as study_population,
    core__condition as DX
where
    study_population.encounter_ref = DX.encounter_ref
;