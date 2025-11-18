create table irae__gpt4_rejection as
select  distinct
        encounter_ref,
        documentreference_ref,
        subject_ref,
        gender,
        race_display,
        age_at_visit,
        enc_start_date,
        doc_date,

        rejection_mentioned	            ,
        rejection_history	            ,
        rejection_present	            ,

        failure_mentioned	            ,
        failure_history	                ,
        failure_present	                ,

        ptld_mentioned	                        ,
        ptld_history	                        ,
        ptld_present	                        ,

        cancer_mentioned	                    ,
        cancer_history	                        ,
        cancer_present	                        ,

from irae__gpt4_fhir;

