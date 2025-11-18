create table irae__cohort_diag_custom as 
select * from 
 irae__cohort_study_population_diag , 
irae__diag_custom
WHERE
irae__cohort_study_population_diag.diag_code = irae__diag_custom.code and 
irae__cohort_study_population_diag.diag_system = irae__diag_custom.system