CREATE TABLE irae__count_patient_lab_gfr AS (
    WITH
    filtered_table AS (
        SELECT
            s.subject_ref,
            --noqa: disable=RF03, AL02
            s."age_at_visit",
            s."gender",
            s."lab_interpretation_display",
            s."lab_observation_code",
            s."race_display",
            s."valueset"
            --noqa: enable=RF03, AL02
        FROM irae__cohort_lab_gfr AS s
    ),
    
    null_replacement AS (
        SELECT
            subject_ref,
            coalesce(
                cast(age_at_visit AS varchar),
                'cumulus__none'
            ) AS age_at_visit,
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
            ) AS lab_observation_code,
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
            "gender",
            "lab_interpretation_display",
            "lab_observation_code",
            "race_display",
            "valueset",
            concat_ws(
                '-',
                COALESCE("age_at_visit",''),
                COALESCE("gender",''),
                COALESCE("lab_interpretation_display",''),
                COALESCE("lab_observation_code",''),
                COALESCE("race_display",''),
                COALESCE("valueset",'')
            ) AS id
        FROM null_replacement
        GROUP BY
            cube(
            "age_at_visit",
            "gender",
            "lab_interpretation_display",
            "lab_observation_code",
            "race_display",
            "valueset"
            )
    )

    SELECT
        p.cnt_subject_ref AS cnt,
        p."age_at_visit",
        p."gender",
        p."lab_interpretation_display",
        p."lab_observation_code",
        p."race_display",
        p."valueset"
    FROM powerset AS p
    WHERE 
        p.cnt_subject_ref >= 10
);