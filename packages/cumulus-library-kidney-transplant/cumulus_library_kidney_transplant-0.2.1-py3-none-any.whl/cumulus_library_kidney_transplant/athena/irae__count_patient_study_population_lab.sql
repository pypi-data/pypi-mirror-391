CREATE TABLE irae__count_patient_study_population_lab AS (
    WITH
    filtered_table AS (
        SELECT
            s.subject_ref,
            --noqa: disable=RF03, AL02
            s."age_at_visit",
            s."enc_class_code",
            s."gender",
            s."lab_interpretation_display",
            s."lab_observation_code"
            --noqa: enable=RF03, AL02
        FROM irae__cohort_study_population_lab AS s
    ),
    
    null_replacement AS (
        SELECT
            subject_ref,
            coalesce(
                cast(age_at_visit AS varchar),
                'cumulus__none'
            ) AS age_at_visit,
            coalesce(
                cast(enc_class_code AS varchar),
                'cumulus__none'
            ) AS enc_class_code,
            coalesce(
                cast(gender AS varchar),
                'cumulus__none'
            ) AS gender,
            coalesce(
                cast(lab_interpretation_display AS varchar),
                'cumulus__none'
            ) AS lab_interpretation_display,
            coalesce(
                cast(lab_observation_code AS varchar),
                'cumulus__none'
            ) AS lab_observation_code
        FROM filtered_table
    ),

    powerset AS (
        SELECT
            count(DISTINCT subject_ref) AS cnt_subject_ref,
            "age_at_visit",
            "enc_class_code",
            "gender",
            "lab_interpretation_display",
            "lab_observation_code",
            concat_ws(
                '-',
                COALESCE("age_at_visit",''),
                COALESCE("enc_class_code",''),
                COALESCE("gender",''),
                COALESCE("lab_interpretation_display",''),
                COALESCE("lab_observation_code",'')
            ) AS id
        FROM null_replacement
        GROUP BY
            cube(
            "age_at_visit",
            "enc_class_code",
            "gender",
            "lab_interpretation_display",
            "lab_observation_code"
            )
    )

    SELECT
        p.cnt_subject_ref AS cnt,
        p."age_at_visit",
        p."enc_class_code",
        p."gender",
        p."lab_interpretation_display",
        p."lab_observation_code"
    FROM powerset AS p
    WHERE 
        p.cnt_subject_ref >= 10
);