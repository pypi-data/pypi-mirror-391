CREATE table irae__sample_casedef_pre as
WITH
encounter_doc as (
    SELECT  distinct
            etl.group_name,
            casedef.subject_ref,
            casedef.encounter_ref,
            doc.documentreference_ref,
            doc.enc_period_ordinal,
            doc.enc_period_start_day,
            doc.doc_author_day,
            doc.doc_date,
            case
            when (doc.doc_author_day    is NOT null)    then doc.doc_author_day
            when (doc.doc_date          is NOT null)    then doc.doc_date
            else doc.enc_period_start_day               end as sort_by_date
    FROM
            etl__completion_encounters              as etl,
            irae__cohort_casedef_pre         as casedef,
            irae__cohort_study_population_doc    as doc
    WHERE
            casedef.encounter_ref   = doc.encounter_ref
    AND     casedef.encounter_ref   = concat('Encounter/', etl.encounter_id)
    ORDER BY
            casedef.subject_ref
), 
ordered as (
    SELECT  distinct
            encounter_doc.*,
            ROW_NUMBER() OVER (
                PARTITION   BY  subject_ref
                ORDER       BY  enc_period_start_day,
                                sort_by_date,
                                documentreference_ref
            )   AS doc_ordinal
    FROM    encounter_doc
)
SELECT
        ordered.*,
        doc.doc_type_code, 
        doc.doc_type_display, 
        doc.doc_type_system
FROM
        ordered,
        irae__cohort_study_population_doc as doc
WHERE
        ordered.documentreference_ref = doc.documentreference_ref
;