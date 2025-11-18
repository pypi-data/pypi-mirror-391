create TABLE irae__cohort_casedef_include as
select  distinct
        irae__cohort_casedef.*
from    irae__cohort_casedef
where   subject_ref not in 
(select  distinct subject_ref from irae__cohort_casedef_exclude); 
