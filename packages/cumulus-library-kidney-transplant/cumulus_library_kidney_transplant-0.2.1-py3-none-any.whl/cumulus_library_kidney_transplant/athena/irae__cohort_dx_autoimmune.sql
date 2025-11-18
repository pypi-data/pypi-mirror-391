create table irae__cohort_dx_autoimmune as 
select * from 
 irae__cohort_study_population_dx , 
irae__dx_autoimmune
WHERE
irae__cohort_study_population_dx.dx_code = irae__dx_autoimmune.code and 
irae__cohort_study_population_dx.dx_system = irae__dx_autoimmune.system