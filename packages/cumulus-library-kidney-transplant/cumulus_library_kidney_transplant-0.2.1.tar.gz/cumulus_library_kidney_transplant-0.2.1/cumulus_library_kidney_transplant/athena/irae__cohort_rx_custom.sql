create table irae__cohort_rx_custom as 
select * from 
 irae__cohort_study_population_rx , 
irae__rx_custom
WHERE
irae__cohort_study_population_rx.rx_code = irae__rx_custom.code and 
irae__cohort_study_population_rx.rx_system = irae__rx_custom.system