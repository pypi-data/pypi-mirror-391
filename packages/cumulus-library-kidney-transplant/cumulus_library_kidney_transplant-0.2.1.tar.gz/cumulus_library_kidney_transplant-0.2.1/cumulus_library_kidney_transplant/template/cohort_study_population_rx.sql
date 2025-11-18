create table $prefix__cohort_study_population_rx as
select distinct
    RX.status               as rx_status,
    RX.category_code        as rx_category_code,
    RX.category_system      as rx_category_system,
    RX.category_display     as rx_category_display,
    RX.medication_code      as rx_code,
    lower(replace(RX.medication_display, chr(10), ' ')) as rx_display,
    RX.medication_system    as rx_system,
    RX.medicationrequest_ref as medicationrequest_ref,
    study_population.*
from
    $prefix__cohort_study_population as study_population,
    core__medicationrequest as RX
where
    study_population.encounter_ref = RX.encounter_ref
;
