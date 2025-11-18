--         documentreference_ref                   ,
--         subject_ref                             ,
--         encounter_ref                           ,
--         enc_start_date                          ,
--         enc_end_date                            ,
--         dsa_is_present	                        ,
--         dsa_mentioned	                        ,
--         dsa_history	                            ,
--         dsa_present	                            ,
--         infection_is_present	                ,
--         infection_mentioned	                    ,
--         infection_history	                    ,
--         infection_present	                    ,
--         viral_is_present	            ,
--         viral_mentioned	            ,
--         viral_history	                ,
--         viral_present	                ,
--         bacterial_is_present	        ,
--         bacterial_mentioned	        ,
--         bacterial_history	            ,
--         bacterial_present	            ,
--         fungal_is_present	            ,
--         fungal_mentioned	            ,
--         fungal_history	            ,
--         fungal_present	            ,
--         rejection_is_present	            ,
--         rejection_mentioned	            ,
--         rejection_history	                ,
--         rejection_present	                ,
--         failure_is_present	            ,
--         failure_mentioned	                ,
--         failure_history	                ,
--         failure_present	                ,
--         ptld_is_present	                        ,
--         ptld_mentioned	                        ,
--         ptld_history	                        ,
--         ptld_present	                        ,
--         cancer_is_present	                    ,
--         cancer_mentioned	                    ,
--         cancer_history	                        ,
--         cancer_present	                        ,
--         error
--

create or replace view irae__gpt4_infection_outcome as
select  distinct
        coalesce(C.rx_compliance_status, 'NoneOfTheAbove') as rx_compliance_status,
        coalesce(C.rx_therapeutic_supra, 0) as rx_therapeutic_supra,
        I.confidence   as infection_confidence,
        I.present_type as infection_type,
        coalesce(RE.rejection_present_best, 'NoneOfTheAbove') as rejection_encounter,
        coalesce(RP.rejection_present_best, 'NoneOfTheAbove') as rejection_patient,
        coalesce(FE.failure_present_best, 'NoneOfTheAbove') as failure_encounter,
        coalesce(FP.failure_present_best, 'NoneOfTheAbove') as failure_patient,
        fhir.subject_ref,
        fhir.encounter_ref,
        fhir.documentreference_ref
from        irae__gpt4_fhir as fhir
left join   irae__gpt4_compliance as C      on fhir.documentreference_ref = C.documentreference_ref
left join   irae__gpt4_infection as I       on fhir.documentreference_ref = I.documentreference_ref
left join   irae__gpt4_failure_enc as FE    on fhir.encounter_ref = FE.encounter_ref
left join   irae__gpt4_failure_pat as FP    on fhir.subject_ref = FP.subject_ref
left join   irae__gpt4_rejection_enc as RE  on fhir.encounter_ref = RE.encounter_ref
left join   irae__gpt4_rejection_pat as RP  on fhir.subject_ref = RP.subject_ref
;
