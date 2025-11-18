CREATE TABLE irae__count_enc_casedef_post_1000_results AS (
    WITH
    filtered_table AS (
        SELECT
            s.subject_ref,
            s.encounter_ref,
            --noqa: disable=RF03, AL02
            s."ade",
            s."age_at_visit",
            s."doc_type_display",
            s."doc_type_system",
            s."enc_class_display",
            s."gender",
            s."period_start_month",
            s."race_display"
            --noqa: enable=RF03, AL02
        FROM irae__cohort_casedef_post_1000_results AS s
        WHERE s.status = 'finished'
    ),
    
    null_replacement AS (
        SELECT
            subject_ref,
            encounter_ref,
            coalesce(
                cast(ade AS varchar),
                'cumulus__none'
            ) AS ade,
            coalesce(
                cast(age_at_visit AS varchar),
                'cumulus__none'
            ) AS age_at_visit,
            coalesce(
                cast(doc_type_display AS varchar),
                'cumulus__none'
            ) AS doc_type_display,
            coalesce(
                cast(doc_type_system AS varchar),
                'cumulus__none'
            ) AS doc_type_system,
            coalesce(
                cast(enc_class_display AS varchar),
                'cumulus__none'
            ) AS enc_class_display,
            coalesce(
                cast(gender AS varchar),
                'cumulus__none'
            ) AS gender,
            coalesce(
                cast(period_start_month AS varchar),
                'cumulus__none'
            ) AS period_start_month,
            coalesce(
                cast(race_display AS varchar),
                'cumulus__none'
            ) AS race_display
        FROM filtered_table
    ),
    secondary_powerset AS (
        SELECT
            count(DISTINCT encounter_ref) AS cnt_encounter_ref,
            "ade",
            "age_at_visit",
            "doc_type_display",
            "doc_type_system",
            "enc_class_display",
            "gender",
            "period_start_month",
            "race_display",
            concat_ws(
                '-',
                COALESCE("ade",''),
                COALESCE("age_at_visit",''),
                COALESCE("doc_type_display",''),
                COALESCE("doc_type_system",''),
                COALESCE("enc_class_display",''),
                COALESCE("gender",''),
                COALESCE("period_start_month",''),
                COALESCE("race_display",'')
            ) AS id
        FROM null_replacement
        GROUP BY
            cube(
            "ade",
            "age_at_visit",
            "doc_type_display",
            "doc_type_system",
            "enc_class_display",
            "gender",
            "period_start_month",
            "race_display"
            )
    ),

    powerset AS (
        SELECT
            count(DISTINCT subject_ref) AS cnt_subject_ref,
            "ade",
            "age_at_visit",
            "doc_type_display",
            "doc_type_system",
            "enc_class_display",
            "gender",
            "period_start_month",
            "race_display",
            concat_ws(
                '-',
                COALESCE("ade",''),
                COALESCE("age_at_visit",''),
                COALESCE("doc_type_display",''),
                COALESCE("doc_type_system",''),
                COALESCE("enc_class_display",''),
                COALESCE("gender",''),
                COALESCE("period_start_month",''),
                COALESCE("race_display",'')
            ) AS id
        FROM null_replacement
        GROUP BY
            cube(
            "ade",
            "age_at_visit",
            "doc_type_display",
            "doc_type_system",
            "enc_class_display",
            "gender",
            "period_start_month",
            "race_display"
            )
    )

    SELECT
        s.cnt_encounter_ref AS cnt,
        p."ade",
        p."age_at_visit",
        p."doc_type_display",
        p."doc_type_system",
        p."enc_class_display",
        p."gender",
        p."period_start_month",
        p."race_display"
    FROM powerset AS p
    JOIN secondary_powerset AS s on s.id = p.id
    WHERE 
        cnt_subject_ref >= 10
);