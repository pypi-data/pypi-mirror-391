create table irae__cohort_dx_cancer as 
select * from 
 irae__cohort_study_population_dx , 
irae__dx_cancer
WHERE
irae__cohort_study_population_dx.dx_code = irae__dx_cancer.code and 
irae__cohort_study_population_dx.dx_system = irae__dx_cancer.system