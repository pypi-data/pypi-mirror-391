create table irae__cohort_dx_infection as 
select * from 
 irae__cohort_study_population_dx , 
irae__dx_infection
WHERE
irae__cohort_study_population_dx.dx_code = irae__dx_infection.code and 
irae__cohort_study_population_dx.dx_system = irae__dx_infection.system