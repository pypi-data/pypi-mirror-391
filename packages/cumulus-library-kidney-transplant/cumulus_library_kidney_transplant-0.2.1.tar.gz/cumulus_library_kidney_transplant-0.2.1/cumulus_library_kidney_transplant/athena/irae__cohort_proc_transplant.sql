create table irae__cohort_proc_transplant as 
select * from 
 irae__cohort_study_population_proc , 
irae__proc_transplant
WHERE
irae__cohort_study_population_proc.proc_code = irae__proc_transplant.code and 
irae__cohort_study_population_proc.proc_system = irae__proc_transplant.system