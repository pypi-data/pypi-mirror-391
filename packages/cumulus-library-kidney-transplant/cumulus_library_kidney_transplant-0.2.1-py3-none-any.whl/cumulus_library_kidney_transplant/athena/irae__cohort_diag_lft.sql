create table irae__cohort_diag_lft as 
select * from 
 irae__cohort_study_population_diag , 
irae__diag_lft
WHERE
irae__cohort_study_population_diag.diag_code = irae__diag_lft.code and 
irae__cohort_study_population_diag.diag_system = irae__diag_lft.system