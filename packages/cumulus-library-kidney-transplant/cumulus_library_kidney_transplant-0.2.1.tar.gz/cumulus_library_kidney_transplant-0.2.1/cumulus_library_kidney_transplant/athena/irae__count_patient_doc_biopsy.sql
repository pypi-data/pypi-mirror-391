CREATE TABLE irae__count_patient_doc_biopsy AS (
    WITH
    filtered_table AS (
        SELECT
            s.subject_ref,
            --noqa: disable=RF03, AL02
            s."age_at_visit",
            s."doc_type_display",
            s."gender",
            s."race_display",
            s."valueset"
            --noqa: enable=RF03, AL02
        FROM irae__cohort_doc_biopsy AS s
    ),
    
    null_replacement AS (
        SELECT
            subject_ref,
            coalesce(
                cast(age_at_visit AS varchar),
                'cumulus__none'
            ) AS age_at_visit,
            coalesce(
                cast(doc_type_display AS varchar),
                'cumulus__none'
            ) AS doc_type_display,
            coalesce(
                cast(gender AS varchar),
                'cumulus__none'
            ) AS gender,
            coalesce(
                cast(race_display AS varchar),
                'cumulus__none'
            ) AS race_display,
            coalesce(
                cast(valueset AS varchar),
                'cumulus__none'
            ) AS valueset
        FROM filtered_table
    ),

    powerset AS (
        SELECT
            count(DISTINCT subject_ref) AS cnt_subject_ref,
            "age_at_visit",
            "doc_type_display",
            "gender",
            "race_display",
            "valueset",
            concat_ws(
                '-',
                COALESCE("age_at_visit",''),
                COALESCE("doc_type_display",''),
                COALESCE("gender",''),
                COALESCE("race_display",''),
                COALESCE("valueset",'')
            ) AS id
        FROM null_replacement
        GROUP BY
            cube(
            "age_at_visit",
            "doc_type_display",
            "gender",
            "race_display",
            "valueset"
            )
    )

    SELECT
        p.cnt_subject_ref AS cnt,
        p."age_at_visit",
        p."doc_type_display",
        p."gender",
        p."race_display",
        p."valueset"
    FROM powerset AS p
    WHERE 
        p.cnt_subject_ref >= 10
);