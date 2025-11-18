CREATE TABLE irae__count_patient_casedef_timeline AS (
    WITH
    filtered_table AS (
        SELECT
            s.subject_ref,
            --noqa: disable=RF03, AL02
            s."age_at_visit",
            s."casedef_period",
            s."enc_period_start_year",
            s."gender"
            --noqa: enable=RF03, AL02
        FROM irae__cohort_casedef_timeline AS s
    ),
    
    null_replacement AS (
        SELECT
            subject_ref,
            coalesce(
                cast(age_at_visit AS varchar),
                'cumulus__none'
            ) AS age_at_visit,
            coalesce(
                cast(casedef_period AS varchar),
                'cumulus__none'
            ) AS casedef_period,
            coalesce(
                cast(enc_period_start_year AS varchar),
                'cumulus__none'
            ) AS enc_period_start_year,
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
            "casedef_period",
            "enc_period_start_year",
            "gender",
            concat_ws(
                '-',
                COALESCE("age_at_visit",''),
                COALESCE("casedef_period",''),
                COALESCE("enc_period_start_year",''),
                COALESCE("gender",'')
            ) AS id
        FROM null_replacement
        GROUP BY
            cube(
            "age_at_visit",
            "casedef_period",
            "enc_period_start_year",
            "gender"
            )
    )

    SELECT
        p.cnt_subject_ref AS cnt,
        p."age_at_visit",
        p."casedef_period",
        p."enc_period_start_year",
        p."gender"
    FROM powerset AS p
    WHERE 
        p.cnt_subject_ref >= 10
);