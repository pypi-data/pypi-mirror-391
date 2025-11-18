create table irae__cohort_lab_diabetes as 
select * from 
 irae__cohort_study_population_lab , 
irae__lab_diabetes
WHERE
irae__cohort_study_population_lab.lab_observation_code = irae__lab_diabetes.code and 
irae__cohort_study_population_lab.lab_observation_system = irae__lab_diabetes.system