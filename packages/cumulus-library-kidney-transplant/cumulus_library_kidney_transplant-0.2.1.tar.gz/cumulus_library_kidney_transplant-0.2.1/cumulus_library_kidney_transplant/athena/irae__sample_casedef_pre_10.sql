create table irae__sample_casedef_pre_10 as
WITH
patient_list as (
    select  distinct
            subject_ref
    from
            irae__sample_casedef_pre
    order by
            subject_ref
    limit
            10
)
select      distinct
            doc.*
from
            irae__sample_casedef_pre as doc,
            patient_list as P
where
            P.subject_ref = doc.subject_ref
order by
            subject_ref,
            enc_period_start_day, 
            doc_author_day;