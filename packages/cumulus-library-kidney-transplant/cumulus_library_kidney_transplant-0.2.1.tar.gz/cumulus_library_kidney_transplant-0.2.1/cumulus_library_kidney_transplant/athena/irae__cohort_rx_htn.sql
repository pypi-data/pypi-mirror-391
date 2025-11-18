create table irae__cohort_rx_htn as 
select * from 
 irae__cohort_study_population_rx , 
irae__rx_htn
WHERE
irae__cohort_study_population_rx.rx_code = irae__rx_htn.code and 
irae__cohort_study_population_rx.rx_system = irae__rx_htn.system