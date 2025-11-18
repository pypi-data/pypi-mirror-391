create TABLE $prefix__cohort_casedef_exclude as WITH
dx_transplant as (
    select  distinct
            valueset, system, code, display,
            subject_ref
    from    $prefix__cohort_dx_transplant
    where   (code, system) not in (select distinct code, system from $prefix__casedef)
    and     CODE not in ('Z94.9', 'V42.9') -- https://github.com/smart-on-fhir/cumulus-library-kidney-transplant/issues/39
),
proc_transplant as (
    select  distinct
            valueset, system, code, display,
            subject_ref
    from    $prefix__cohort_proc_transplant
    where  (code, system) not in (select distinct code, system from $prefix__casedef)
),
first_visit as
(
    select  min(enc_period_start_day) as index_date,
            subject_ref
    from    $prefix__cohort_casedef
    where   include
    group by subject_ref
),
complication as
(
    select  min(enc_period_start_day) as index_date,
            subject_ref, valueset, code, display, system
    from    $prefix__cohort_casedef
    where   NOT include
    group by subject_ref, valueset, code, display, system
),
first_visit_complication as
(
    select  distinct
            valueset, system, code, display,
            complication.subject_ref
    from    first_visit, complication
    where   first_visit.subject_ref = complication.subject_ref
    and     first_visit.index_date > complication.index_date
),
exclusion_list as (
    select * from dx_transplant
    UNION ALL
    select * from proc_transplant
    UNION ALL
    select * from first_visit_complication
)
select  distinct
        exclusion_list.*
from    exclusion_list,
        $prefix__cohort_casedef as casedef
where   exclusion_list.subject_ref = casedef.subject_ref
;