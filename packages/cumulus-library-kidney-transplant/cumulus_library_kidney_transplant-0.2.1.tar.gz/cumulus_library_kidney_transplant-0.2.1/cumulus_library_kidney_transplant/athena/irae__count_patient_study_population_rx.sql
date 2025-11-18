CREATE TABLE irae__count_patient_study_population_rx AS (
    WITH
    filtered_table AS (
        SELECT
            s.subject_ref,
            --noqa: disable=RF03, AL02
            s."age_at_visit",
            s."enc_class_code",
            s."gender",
            s."rx_category_code",
            s."rx_display"
            --noqa: enable=RF03, AL02
        FROM irae__cohort_study_population_rx AS s
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
                cast(rx_category_code AS varchar),
                'cumulus__none'
            ) AS rx_category_code,
            coalesce(
                cast(rx_display AS varchar),
                'cumulus__none'
            ) AS rx_display
        FROM filtered_table
    ),

    powerset AS (
        SELECT
            count(DISTINCT subject_ref) AS cnt_subject_ref,
            "age_at_visit",
            "enc_class_code",
            "gender",
            "rx_category_code",
            "rx_display",
            concat_ws(
                '-',
                COALESCE("age_at_visit",''),
                COALESCE("enc_class_code",''),
                COALESCE("gender",''),
                COALESCE("rx_category_code",''),
                COALESCE("rx_display",'')
            ) AS id
        FROM null_replacement
        GROUP BY
            cube(
            "age_at_visit",
            "enc_class_code",
            "gender",
            "rx_category_code",
            "rx_display"
            )
    )

    SELECT
        p.cnt_subject_ref AS cnt,
        p."age_at_visit",
        p."enc_class_code",
        p."gender",
        p."rx_category_code",
        p."rx_display"
    FROM powerset AS p
    WHERE 
        p.cnt_subject_ref >= 10
);