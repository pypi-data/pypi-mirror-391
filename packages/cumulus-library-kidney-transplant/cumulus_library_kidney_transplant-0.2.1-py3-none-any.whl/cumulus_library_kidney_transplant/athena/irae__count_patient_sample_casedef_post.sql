CREATE TABLE irae__count_patient_sample_casedef_post AS (
    WITH
    filtered_table AS (
        SELECT
            s.subject_ref,
            --noqa: disable=RF03, AL02
            s."doc_type_code",
            s."doc_type_display",
            s."doc_type_system",
            s."group_name"
            --noqa: enable=RF03, AL02
        FROM irae__sample_casedef_post AS s
    ),
    
    null_replacement AS (
        SELECT
            subject_ref,
            coalesce(
                cast(doc_type_code AS varchar),
                'cumulus__none'
            ) AS doc_type_code,
            coalesce(
                cast(doc_type_display AS varchar),
                'cumulus__none'
            ) AS doc_type_display,
            coalesce(
                cast(doc_type_system AS varchar),
                'cumulus__none'
            ) AS doc_type_system,
            coalesce(
                cast(group_name AS varchar),
                'cumulus__none'
            ) AS group_name
        FROM filtered_table
    ),

    powerset AS (
        SELECT
            count(DISTINCT subject_ref) AS cnt_subject_ref,
            "doc_type_code",
            "doc_type_display",
            "doc_type_system",
            "group_name",
            concat_ws(
                '-',
                COALESCE("doc_type_code",''),
                COALESCE("doc_type_display",''),
                COALESCE("doc_type_system",''),
                COALESCE("group_name",'')
            ) AS id
        FROM null_replacement
        GROUP BY
            cube(
            "doc_type_code",
            "doc_type_display",
            "doc_type_system",
            "group_name"
            )
    )

    SELECT
        p.cnt_subject_ref AS cnt,
        p."doc_type_code",
        p."doc_type_display",
        p."doc_type_system",
        p."group_name"
    FROM powerset AS p
    WHERE 
        p.cnt_subject_ref >= 10
);