create table irae__cohort_rx_immunosuppressive as 
select * from 
 irae__cohort_study_population_rx , 
irae__rx_immunosuppressive
WHERE
irae__cohort_study_population_rx.rx_code = irae__rx_immunosuppressive.code and 
irae__cohort_study_population_rx.rx_system = irae__rx_immunosuppressive.system