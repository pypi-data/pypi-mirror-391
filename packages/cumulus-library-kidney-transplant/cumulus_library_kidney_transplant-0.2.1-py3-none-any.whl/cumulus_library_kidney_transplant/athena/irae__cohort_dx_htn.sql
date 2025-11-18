create table irae__cohort_dx_htn as 
select * from 
 irae__cohort_study_population_dx , 
irae__dx_htn
WHERE
irae__cohort_study_population_dx.dx_code = irae__dx_htn.code and 
irae__cohort_study_population_dx.dx_system = irae__dx_htn.system