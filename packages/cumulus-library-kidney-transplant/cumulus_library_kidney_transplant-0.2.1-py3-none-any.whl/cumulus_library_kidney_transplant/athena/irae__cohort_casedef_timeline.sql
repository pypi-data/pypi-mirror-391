-- Timeline with "sequence of events" (soe) of patients matching case definition
--
create or replace view irae__cohort_casedef_timeline as
select 'pre'   as casedef_period, * from irae__cohort_casedef_pre
UNION ALL
select 'index' as casedef_period, * from irae__cohort_casedef_index
UNION ALL
select 'post'  as casedef_period, * from irae__cohort_casedef_post
;