-- ###########################################################################
-- Raw VS FHIR linked data matches

select  count(distinct filename) as cnt_documents,
        count(*) as cnt_rows
from    irae__gpt4_raw;

--     cnt_documents	cnt_rows
--     33117	        33117

select  count(distinct subject_ref)             as cnt_patients,
        count(distinct documentreference_ref)   as cnt_documents,
        count(distinct encounter_ref)           as cnt_encounters
from    irae__gpt4_fhir;

--     cnt_patients cnt_documents   cnt_encounters
--     218	        33116	        10506


select count(*) from irae__gpt4_fhir where dsa_is_present!=dsa_mentioned;
--     75 (0.2% compared to 32406)


with patient_variable as
(
    select  distinct subject_ref,
            donor_type as variable
    from irae__gpt4_parsed
)
select  count(distinct subject_ref) as cnt_patients,
        variable
from    patient_variable
group by variable
order by cnt_patients desc;


with only_year as
(
    select  distinct fhir_ref from irae__gpt4_term_freq_first
    where   col = 'donor_date'
    and     fhir_ref like 'Patient/%'
    and     date(val) < date('1980-01-01')
)
select tf.*
from
    only_year,
    irae__gpt4_term_freq_all as tf
where   only_year.fhir_ref = tf.fhir_ref
and     tf.col = 'donor_date'
order by tf.fhir_ref, tf.cnt desc
