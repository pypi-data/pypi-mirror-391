CREATE TABLE irae__count_patient_study_population_doc AS (
    WITH
    filtered_table AS (
        SELECT
            s.subject_ref,
            --noqa: disable=RF03, AL02
            s."age_at_visit",
            s."doc_type_display",
            s."enc_class_code",
            s."gender"
            --noqa: enable=RF03, AL02
        FROM irae__cohort_study_population_doc AS s
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
                cast(enc_class_code AS varchar),
                'cumulus__none'
            ) AS enc_class_code,
            coalesce(
                cast(gender AS varchar),
                'cumulus__none'
            ) AS gender
        FROM filtered_table
    ),

    powerset AS (
        SELECT
            count(DISTINCT subject_ref) AS cnt_subject_ref,
            "age_at_visit",
            "doc_type_display",
            "enc_class_code",
            "gender",
            concat_ws(
                '-',
                COALESCE("age_at_visit",''),
                COALESCE("doc_type_display",''),
                COALESCE("enc_class_code",''),
                COALESCE("gender",'')
            ) AS id
        FROM null_replacement
        GROUP BY
            cube(
            "age_at_visit",
            "doc_type_display",
            "enc_class_code",
            "gender"
            )
    )

    SELECT
        p.cnt_subject_ref AS cnt,
        p."age_at_visit",
        p."doc_type_display",
        p."enc_class_code",
        p."gender"
    FROM powerset AS p
    WHERE 
        p.cnt_subject_ref >= 10
);