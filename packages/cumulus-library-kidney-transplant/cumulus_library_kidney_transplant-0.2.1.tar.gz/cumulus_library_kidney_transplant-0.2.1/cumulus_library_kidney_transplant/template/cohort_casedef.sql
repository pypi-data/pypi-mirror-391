create table    $prefix__cohort_casedef as
select  distinct
        'casedef_dx'    as valueset,
        condition_ref   as resource_ref,
        enc_period_ordinal,
        enc_period_start_day,
        age_at_visit,
        subject_ref,
        encounter_ref,
        casedef.*
from    $prefix__casedef   as casedef,
        $prefix__cohort_study_population_dx
where   casedef.system  = dx_system
and     casedef.code    = dx_code

UNION ALL
select  distinct
        'casedef_proc'  as valueset,
        procedure_ref   as resource_ref,
        enc_period_ordinal,
        enc_period_start_day,
        age_at_visit,
        subject_ref,
        encounter_ref,
        casedef.*
from    $prefix__casedef   as casedef,
        $prefix__cohort_study_population_proc
where   casedef.system  = proc_system
and     casedef.code    = proc_code

UNION ALL
select  distinct
        'casedef_lab'   as valueset,
        observation_ref as resource_ref,
        enc_period_ordinal,
        enc_period_start_day,
        age_at_visit,
        subject_ref,
        encounter_ref,
        casedef.*
from    $prefix__casedef   as casedef,
        $prefix__cohort_study_population_lab
where   casedef.system  = lab_observation_system
and     casedef.code    = lab_observation_code

UNION ALL
select  distinct
        'casedef_rx'            as valueset,
        medicationrequest_ref   as resource_ref,
        enc_period_ordinal,
        enc_period_start_day,
        age_at_visit,
        subject_ref,
        encounter_ref,
        casedef.*
from    $prefix__casedef           as casedef,
        $prefix__cohort_study_population_rx
where   casedef.system  = rx_system
and     casedef.code    = rx_code

UNION ALL
select  distinct
        'casedef_diag'  as valueset,
        result_ref      as resource_ref,
        enc_period_ordinal,
        enc_period_start_day,
        age_at_visit,
        subject_ref,
        encounter_ref,
        casedef.*
from    $prefix__casedef   as casedef,
        $prefix__cohort_study_population_diag
where   casedef.system  = diag_code_system
and     casedef.code    = diag_code

UNION ALL
select  distinct
        'casedef_doc'           as valueset,
        documentreference_ref   as resource_ref,
        enc_period_ordinal,
        enc_period_start_day,
        age_at_visit,
        subject_ref,
        encounter_ref,
        casedef.*
from    $prefix__casedef           as casedef,
        $prefix__cohort_study_population_doc
where   casedef.system  = doc_type_system
and     casedef.code    = doc_type_code
;

