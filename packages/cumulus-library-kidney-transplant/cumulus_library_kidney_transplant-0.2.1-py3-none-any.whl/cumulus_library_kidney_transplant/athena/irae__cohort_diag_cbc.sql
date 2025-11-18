create table irae__cohort_diag_cbc as 
select * from 
 irae__cohort_study_population_diag , 
irae__diag_cbc
WHERE
irae__cohort_study_population_diag.diag_code = irae__diag_cbc.code and 
irae__cohort_study_population_diag.diag_system = irae__diag_cbc.system