create TABLE $prefix__cohort_casedef_include as
select  distinct
        $prefix__cohort_casedef.*
from    $prefix__cohort_casedef
where   subject_ref not in 
(select  distinct subject_ref from $prefix__cohort_casedef_exclude); 
