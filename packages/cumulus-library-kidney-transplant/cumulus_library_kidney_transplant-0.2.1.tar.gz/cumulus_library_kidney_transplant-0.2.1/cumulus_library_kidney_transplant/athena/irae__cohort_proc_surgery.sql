create table irae__cohort_proc_surgery as 
select * from 
 irae__cohort_study_population_proc , 
irae__proc_surgery
WHERE
irae__cohort_study_population_proc.proc_code = irae__proc_surgery.code and 
irae__cohort_study_population_proc.proc_system = irae__proc_surgery.system