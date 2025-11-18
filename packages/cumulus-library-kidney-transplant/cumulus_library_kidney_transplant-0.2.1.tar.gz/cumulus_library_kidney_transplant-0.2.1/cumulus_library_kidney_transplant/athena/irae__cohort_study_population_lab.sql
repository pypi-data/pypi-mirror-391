-- https://github.com/smart-on-fhir/cumulus-library/issues/340
-- select from core__observation to include interpretation and value

create table irae__cohort_study_population_lab as
select distinct
    lab.status                      as lab_status,
    observation_code                as lab_observation_code,
    observation_system              as lab_observation_system,
    valuecodeableconcept_code       as lab_concept_code,
    valuecodeableconcept_display    as lab_concept_display,
    valuecodeableconcept_system     as lab_concept_system,
    effectivedatetime_day           as lab_effectivedate,
    interpretation_code             as lab_interpretation_code,
    interpretation_system           as lab_interpretation_system,
    interpretation_display          as lab_interpretation_display,
    valuequantity_value             as lab_valuequantity_value,
    valuequantity_comparator        as lab_valuequantity_comparator,
    valuequantity_unit              as lab_valuequantity_unit,
    valuequantity_system            as lab_valuequantity_system,
    valuequantity_code              as lab_valuequantity_code,
    valuestring                     as lab_valuestring,
    observation_ref,
    study_population.*
from
    irae__cohort_study_population as study_population,
    core__observation as lab
where
    lab.category_code = 'laboratory' and
    study_population.encounter_ref = lab.encounter_ref
;