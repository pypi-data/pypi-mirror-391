CREATE TABLE irae__cohort_study_period as
WITH
range as (
    select  distinct
            E.subject_ref,
            E.period_start_day,
            E.period_end_day,
            E.encounter_ref
    from
            core__encounter             as E,
            irae__include_study_period  as include
    where
            (E.period_start_day between include.period_start and include.period_end)
            and
            (E.period_end_day   between include.period_start and include.period_end)
            and
            (E.period_start_day < CURRENT_DATE)
),
history as (
    SELECT  DISTINCT
            E.subject_ref,
            E.period_start_day,
            E.period_end_day,
            E.encounter_ref
    FROM
            core__encounter             as E
    JOIN
            irae__include_study_period  as include
      ON    include.include_history
     AND    e.period_start_day < include.period_start
    WHERE   EXISTS  (
            SELECT  1
            FROM    range
            WHERE   range.subject_ref = E.subject_ref)
),
merged as (
    select  *  from range
    UNION ALL
    select  *  from history
),
uniq as (
    SELECT  distinct
            subject_ref,
            period_start_day,
            period_end_day
    from    merged
),
ordinal as (
    SELECT  distinct
            subject_ref,
            period_start_day,
            period_end_day,
            ROW_NUMBER() OVER (
                PARTITION   BY  subject_ref
                ORDER       BY  period_start_day    NULLS LAST,
                                period_end_day      NULLS LAST
            )   AS period_ordinal
    FROM    uniq
)
select  distinct
        ordinal.subject_ref,
        ordinal.period_ordinal,
        ordinal.period_start_day,
        ordinal.period_end_day,
        merged.encounter_ref
from    merged,
        ordinal
where   merged.subject_ref       = ordinal.subject_ref
and     merged.period_start_day  = ordinal.period_start_day
and     merged.period_end_day    = ordinal.period_end_day
;