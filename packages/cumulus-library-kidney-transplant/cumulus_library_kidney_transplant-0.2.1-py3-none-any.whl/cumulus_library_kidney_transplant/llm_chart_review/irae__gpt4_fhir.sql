create table irae__gpt4_fhir as
select  distinct
        E.class_code        as enc_class_code,
        E.class_display     as enc_class_display,
        E.period_start_day  as enc_start_date,
        E.period_end_day    as enc_end_date,
        E.gender            as gender,
        E.race_display      as race_display,
        E.age_at_visit      as age_at_visit,
        DOC.date            as doc_date,
        DOC.author_day      as doc_author_date,
        DOC.type_code       as doc_type_code,
        DOC.type_display    as doc_type_display,
        DOC.encounter_ref,
        GPT4.*
from    irae__gpt4_parsed       as GPT4,
        core__documentreference as DOC,
        core__encounter         as E
where   DOC.encounter_ref = E.encounter_ref
and     DOC.documentreference_ref = GPT4.documentreference_ref
order by GPT4.subject_ref, enc_start_date, enc_end_date, encounter_ref;
