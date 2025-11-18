create or replace view irae__gpt4_donor_vars as
select  distinct
        encounter_ref,
        documentreference_ref,
        subject_ref,
        gender,
        race_display,
        age_at_visit,
        enc_start_date,
        doc_date,
        donor_date_mentioned,
        doc_type_display,
        donor_type,
        donor_type_mentioned,
        donor_date,
        donor_relationship,
        donor_relationship_mentioned,
        donor_hla_quality,
        donor_hla_mismatch
from irae__gpt4_fhir;

create or replace view irae__gpt4_donor as
       select   distinct
                var.encounter_ref,
                var.documentreference_ref,
                var.subject_ref,
                var.gender,
                var.race_display,
                var.age_at_visit,
                var.enc_start_date,
                var.doc_date,
                var.donor_date_mentioned,
                var.doc_type_display,
                coalesce(join_type.donor_type_best, 'NotMentioned') as donor_type_best,
                var.donor_type,
                var.donor_type_mentioned,
                var.donor_date,
                coalesce(join_relate.donor_relationship_best, 'NotMentioned') as donor_relationship_best,
                var.donor_relationship,
                var.donor_relationship_mentioned,
                var.donor_hla_quality,
                var.donor_hla_mismatch,
                join_date.donor_date_best,
                date_trunc('month', join_date.donor_date_best) as donor_date_best_month,
                date_trunc('year', join_date.donor_date_best) as donor_date_best_year
       from     irae__gpt4_donor_vars   as  var
           left join irae__gpt4_donor_date as join_date on var.subject_ref = join_date.subject_ref
           left join irae__gpt4_donor_type as join_type  on var.subject_ref = join_type.subject_ref
           left join irae__gpt4_donor_relationship as join_relate on var.subject_ref = join_relate.subject_ref;
