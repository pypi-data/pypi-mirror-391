create or replace view irae__gpt4_summary as
select  distinct
        encounter_ref                       ,
        documentreference_ref               ,
        subject_ref                         ,
        enc_start_date                      ,
        enc_end_date                        ,
        doc_date,
        donor_type	                        ,
        donor_relationship	                ,
        donor_hla_quality	                ,
        donor_hla_mismatch	                ,
        rx_therapeutic_level	            ,
        rx_therapeutic_sub	                ,
        rx_therapeutic_supra	            ,
        rx_compliance_level	                ,
        rx_compliance_partial	            ,
        rx_compliance_non	                ,
        dsa_present                         ,
        viral_present	                    ,
        infection_present	                ,
        bacterial_present	                ,
        fungal_present	                    ,
        rejection_present	                ,
        failure_present	                    ,
        cancer_present	                    ,
        ptld_present                        ,
        error_found
from    irae__gpt4_fhir    as GPT4;


