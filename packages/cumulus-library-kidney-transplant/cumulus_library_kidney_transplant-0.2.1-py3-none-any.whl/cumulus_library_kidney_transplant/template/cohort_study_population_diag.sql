-- https://github.com/smart-on-fhir/cumulus-library/issues/340

--    LOINC
--    ##############################################
--    LP75011-4 Lab     (Laboratory)
--    LP7819-8  MICRO   (Microbiology)
--    LP7839-6  PATH    (Pathology)
--    LP29684-5 RAD     (Radiology)
--    LP29708-2 Card    (Cardiology)

--    http://terminology.hl7.org/CodeSystem/v2-0074
--    ##############################################
--    BG	Blood Gases
--    BLB	Blood Bank
--    CH	Chemistry
--    GE	Genetics
--    HM	Hematology
--    LAB	Laboratory
--    MB	Microbiology
--    RAD	Radiology

--    ##############################################

create table $prefix__cohort_study_population_diag as
with study_diag as  (
 select distinct
    	diag.status                     as diag_status,
    	diag.category_code              as diag_category_code,
    	diag.category_system            as diag_category_system,
    	diag.category_display           as diag_category_display,
    	diag.code_code                  as diag_code,
    	diag.code_system                as diag_code_system,
    	diag.code_display               as diag_code_display,
    	diag.effectivedatetime_day      as diag_effectivedatetime_day,
    	diag.result_ref,
    	study_population.*
	from
    	$prefix__cohort_study_population as study_population,
    	core__diagnosticreport as diag
	where
	    study_population.encounter_ref = diag.encounter_ref
)
select distinct 
        study_diag.*, 
        obs.interpretation_code         as obs_interpretation_code,
        obs.interpretation_system       as obs_interpretation_system,
        obs.interpretation_display      as obs_interpretation_display,
        obs.valuequantity_value         as obs_valuequantity_value,
        obs.valuequantity_comparator    as obs_valuequantity_comparator,
        obs.valuequantity_unit          as obs_valuequantity_unit,
        obs.valuequantity_system        as obs_valuequantity_system,
        obs.valuequantity_code          as obs_valuequantity_code,
        obs.valuestring                 as obs_valuestring
from    study_diag
left join
        core__observation as obs
    on  study_diag.result_ref = obs.observation_ref