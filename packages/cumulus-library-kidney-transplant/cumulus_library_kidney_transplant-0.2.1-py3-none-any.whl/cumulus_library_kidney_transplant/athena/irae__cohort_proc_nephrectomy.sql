create table irae__cohort_proc_nephrectomy as 
select * from 
 irae__cohort_study_population_proc , 
irae__proc_nephrectomy
WHERE
irae__cohort_study_population_proc.proc_code = irae__proc_nephrectomy.code and 
irae__cohort_study_population_proc.proc_system = irae__proc_nephrectomy.system