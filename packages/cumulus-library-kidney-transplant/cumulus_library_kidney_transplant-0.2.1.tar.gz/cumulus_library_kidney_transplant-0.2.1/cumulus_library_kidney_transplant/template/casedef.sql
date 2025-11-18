create or replace view $prefix__casedef as
with cast_type_safe as (
    select distinct
        system,
        replace(code, '@', '')  as code,
        display,
        likely      = 'true'    as likely,
        preop       = 'true'    as preop,
        transplant  = 'true'    as transplant,
        rejection   = 'true'    as rejection,
        failure     = 'true'    as failure,
        outcome     = 'true'    as outcome,
        lab         = 'true'    as lab,
        imaging     = 'true'    as imaging
    from $prefix__casedef_custom_csv
),
include_first_visit as (
    select  distinct
            cast_type_safe.*,
            True as include
    from    cast_type_safe
    where   likely
    or      preop
    or      transplant
    or      imaging
),
exclude_first_visit as (
    select  distinct
            cast_type_safe.*,
            False as include
    from    cast_type_safe
    where   rejection
    or      failure
    or      outcome
)
select * from include_first_visit
UNION
select * from exclude_first_visit
;