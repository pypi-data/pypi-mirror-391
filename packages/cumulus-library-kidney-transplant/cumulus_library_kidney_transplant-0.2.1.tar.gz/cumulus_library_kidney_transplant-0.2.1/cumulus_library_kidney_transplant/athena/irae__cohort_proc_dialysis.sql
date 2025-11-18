create table irae__cohort_proc_dialysis as 
select * from 
 irae__cohort_study_population_proc , 
irae__proc_dialysis
WHERE
irae__cohort_study_population_proc.proc_code = irae__proc_dialysis.code and 
irae__cohort_study_population_proc.proc_system = irae__proc_dialysis.system