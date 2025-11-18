--         encounter_ref,
--         documentreference_ref,
--         subject_ref,
--         gender,
--         race_display,
--         age_at_visit,
--         enc_start_date,
--         doc_date,
--         rejection_mentioned	            ,
--         rejection_history	            ,
--         rejection_present	            ,
--         failure_mentioned	            ,
--         failure_history	                ,
--         failure_present

create or replace view irae__gpt4_failure_ever as
select  distinct
        rank.code as failure_present,
        rank.ranking ,
        encounter_ref, subject_ref
from    irae__gpt4_fhir as gpt4,
        irae__ranking as rank
where   rank.code = gpt4.failure_present;

create or replace view irae__gpt4_failure_pat as
WITH    value_counts as (
	    select  subject_ref, failure_present, max(ranking) as rank_max
	    from    irae__gpt4_failure_ever as ever_present
	    group by subject_ref, failure_present
),
best as (
	select subject_ref, failure_present, rank_max,
	row_number() over ( partition by subject_ref order by rank_max DESC, failure_present ASC) as rn
	from value_counts )
SELECT  distinct
        subject_ref, failure_present as failure_present_best, rank_max
from    best
where rn =1
order by subject_ref;


create or replace view irae__gpt4_failure_enc as
WITH value_counts as (
	select  encounter_ref, failure_present, max(ranking) as rank_max
	from    irae__gpt4_failure_ever as ever_present
	group by encounter_ref, failure_present
),
best as (
	select encounter_ref, failure_present, rank_max,
	row_number() over ( partition by encounter_ref order by rank_max DESC, failure_present ASC) as rn
	from value_counts )
SELECT  distinct
        encounter_ref, failure_present as failure_present_best, rank_max
from    best
where rn =1
order by encounter_ref;


create or replace view irae__gpt4_failure as
select  ever_present.*,
        coalesce(E.failure_present_best, 'NoneOfTheAbove')    as failure_encounter,
        coalesce(P.failure_present_best, 'NoneOfTheAbove')    as failure_patient
from        irae__gpt4_failure_ever as ever_present
left join   irae__gpt4_failure_enc as E on ever_present.encounter_ref = E.encounter_ref
left join   irae__gpt4_failure_pat as P on ever_present.subject_ref = P.subject_ref
order by ever_present.subject_ref, ever_present.encounter_ref
;