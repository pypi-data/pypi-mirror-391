create table $prefix__cohort_multi_$variable as
select  distinct
        dx.valueset as dx_valueset,
        dx.dx_category_code,
        dx.dx_code,
        dx.dx_system,
        dx.dx_display,
        dx.age_at_visit,
        dx.gender,
        lab.valueset as lab_valueset,
        lab.lab_observation_code,
        lab.lab_observation_system,
        lab.lab_concept_code,
        lab.lab_concept_display,
        lab.lab_concept_system,
        lab.lab_effectivedate,
        lab.lab_interpretation_code,
        lab.lab_interpretation_system,
        lab.lab_interpretation_display,
        lab.lab_valuequantity_value,
        lab.lab_valuequantity_comparator,
        lab.lab_valuequantity_unit,
        lab.lab_valuequantity_system,
        lab.lab_valuequantity_code,
        lab.lab_valuestring,
        rx.valueset as rx_valueset,
        rx.rx_category_code,
        rx.rx_category_system,
        rx.rx_category_display,
        rx.rx_code,
        dx.condition_ref,
        dx.encounter_ref,
        dx.subject_ref
from    $prefix__cohort_dx_$variable    as dx,
        $prefix__cohort_lab_$variable   as lab,
        $prefix__cohort_rx_$variable    as rx
where   dx.encounter_ref = lab.encounter_ref
and     dx.encounter_ref = rx.encounter_ref


