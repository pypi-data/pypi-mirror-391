create table irae__cohort_lab_custom as 
select * from 
 irae__cohort_study_population_lab , 
irae__lab_custom
WHERE
irae__cohort_study_population_lab.lab_observation_code = irae__lab_custom.code and 
irae__cohort_study_population_lab.lab_observation_system = irae__lab_custom.system