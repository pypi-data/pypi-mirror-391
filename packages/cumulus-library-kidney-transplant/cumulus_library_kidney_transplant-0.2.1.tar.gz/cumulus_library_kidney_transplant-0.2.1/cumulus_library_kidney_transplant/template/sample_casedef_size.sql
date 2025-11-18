create table $prefix__sample_casedef_$period_$size as
WITH
patient_list as (
    select  distinct
            subject_ref
    from
            $prefix__sample_casedef_$period
    order by
            subject_ref
    limit
            $size
)
select      distinct
            doc.*
from
            $prefix__sample_casedef_$period as doc,
            patient_list as P
where
            P.subject_ref = doc.subject_ref
order by
            subject_ref,
            enc_period_start_day, 
            doc_author_day;