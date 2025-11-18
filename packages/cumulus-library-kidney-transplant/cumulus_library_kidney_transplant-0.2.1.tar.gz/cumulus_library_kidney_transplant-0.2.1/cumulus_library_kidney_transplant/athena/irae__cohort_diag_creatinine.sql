create table irae__cohort_diag_creatinine as 
select * from 
 irae__cohort_study_population_diag , 
irae__diag_creatinine
WHERE
irae__cohort_study_population_diag.diag_code = irae__diag_creatinine.code and 
irae__cohort_study_population_diag.diag_system = irae__diag_creatinine.system