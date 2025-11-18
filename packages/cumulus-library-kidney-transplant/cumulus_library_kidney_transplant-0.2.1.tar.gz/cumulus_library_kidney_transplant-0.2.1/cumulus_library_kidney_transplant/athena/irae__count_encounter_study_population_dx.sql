CREATE TABLE irae__count_encounter_study_population_dx AS (
    WITH
    filtered_table AS (
        SELECT
            s.subject_ref,
            s.encounter_ref,
            --noqa: disable=RF03, AL02
            s."age_at_visit",
            s."dx_category_code",
            s."dx_display",
            s."enc_class_code",
            s."gender"
            --noqa: enable=RF03, AL02
        FROM irae__cohort_study_population_dx AS s
        WHERE s.status = 'finished'
    ),
    
    null_replacement AS (
        SELECT
            subject_ref,
            encounter_ref,
            coalesce(
                cast(age_at_visit AS varchar),
                'cumulus__none'
            ) AS age_at_visit,
            coalesce(
                cast(dx_category_code AS varchar),
                'cumulus__none'
            ) AS dx_category_code,
            coalesce(
                cast(dx_display AS varchar),
                'cumulus__none'
            ) AS dx_display,
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
    secondary_powerset AS (
        SELECT
            count(DISTINCT encounter_ref) AS cnt_encounter_ref,
            "age_at_visit",
            "dx_category_code",
            "dx_display",
            "enc_class_code",
            "gender",
            concat_ws(
                '-',
                COALESCE("age_at_visit",''),
                COALESCE("dx_category_code",''),
                COALESCE("dx_display",''),
                COALESCE("enc_class_code",''),
                COALESCE("gender",'')
            ) AS id
        FROM null_replacement
        WHERE encounter_ref IS NOT NULL
        GROUP BY
            cube(
            "age_at_visit",
            "dx_category_code",
            "dx_display",
            "enc_class_code",
            "gender"
            )
    ),

    powerset AS (
        SELECT
            count(DISTINCT subject_ref) AS cnt_subject_ref,
            "age_at_visit",
            "dx_category_code",
            "dx_display",
            "enc_class_code",
            "gender",
            concat_ws(
                '-',
                COALESCE("age_at_visit",''),
                COALESCE("dx_category_code",''),
                COALESCE("dx_display",''),
                COALESCE("enc_class_code",''),
                COALESCE("gender",'')
            ) AS id
        FROM null_replacement
        GROUP BY
            cube(
            "age_at_visit",
            "dx_category_code",
            "dx_display",
            "enc_class_code",
            "gender"
            )
    )

    SELECT
        s.cnt_encounter_ref AS cnt,
        p."age_at_visit",
        p."dx_category_code",
        p."dx_display",
        p."enc_class_code",
        p."gender"
    FROM powerset AS p
    JOIN secondary_powerset AS s on s.id = p.id
    WHERE 
        p.cnt_subject_ref >= 10
        AND s.cnt_encounter_ref >= 10
);