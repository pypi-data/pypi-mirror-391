CREATE TABLE irae__count_patient_study_variables AS (
    WITH
    filtered_table AS (
        SELECT
            s.subject_ref,
            --noqa: disable=RF03, AL02
            s."age_at_visit",
            s."gender",
            s."race_display",
            s."valueset",
            s."variable"
            --noqa: enable=RF03, AL02
        FROM irae__cohort_study_variables AS s
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
                cast(race_display AS varchar),
                'cumulus__none'
            ) AS race_display,
            coalesce(
                cast(valueset AS varchar),
                'cumulus__none'
            ) AS valueset,
            coalesce(
                cast(variable AS varchar),
                'cumulus__none'
            ) AS variable
        FROM filtered_table
    ),

    powerset AS (
        SELECT
            count(DISTINCT subject_ref) AS cnt_subject_ref,
            "age_at_visit",
            "gender",
            "race_display",
            "valueset",
            "variable",
            concat_ws(
                '-',
                COALESCE("age_at_visit",''),
                COALESCE("gender",''),
                COALESCE("race_display",''),
                COALESCE("valueset",''),
                COALESCE("variable",'')
            ) AS id
        FROM null_replacement
        GROUP BY
            cube(
            "age_at_visit",
            "gender",
            "race_display",
            "valueset",
            "variable"
            )
    )

    SELECT
        p.cnt_subject_ref AS cnt,
        p."age_at_visit",
        p."gender",
        p."race_display",
        p."valueset",
        p."variable"
    FROM powerset AS p
    WHERE 
        p.cnt_subject_ref >= 10
);