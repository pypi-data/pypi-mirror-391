CREATE TABLE irae__count_document_study_population_doc AS (
    WITH
    filtered_table AS (
        SELECT
            s.subject_ref,
            s.documentreference_ref,
            e.class_display,
            --noqa: disable=RF03, AL02
            s."age_at_visit",
            s."doc_type_display",
            s."enc_class_code",
            s."gender"
            --noqa: enable=RF03, AL02
        FROM irae__cohort_study_population_doc AS s
        INNER JOIN core__encounter AS e
            ON s.encounter_ref = e.encounter_ref
    ),
    
    null_replacement AS (
        SELECT
            subject_ref,
            documentreference_ref,
            coalesce(
                cast(class_display AS varchar), 
                'cumulus__none'
            ) AS class_display,
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
    secondary_powerset AS (
        SELECT
            count(DISTINCT documentreference_ref) AS cnt_documentreference_ref,
            "age_at_visit",
            "doc_type_display",
            "enc_class_code",
            "gender",
            class_display
            ,
            concat_ws(
                '-',
                COALESCE("age_at_visit",''),
                COALESCE("doc_type_display",''),
                COALESCE("enc_class_code",''),
                COALESCE("gender",''),
                COALESCE(class_display,'')
                
            ) AS id
        FROM null_replacement
        WHERE documentreference_ref IS NOT NULL
        GROUP BY
            cube(
            "age_at_visit",
            "doc_type_display",
            "enc_class_code",
            "gender",
            class_display
            
            )
    ),

    powerset AS (
        SELECT
            count(DISTINCT subject_ref) AS cnt_subject_ref,
            "age_at_visit",
            "doc_type_display",
            "enc_class_code",
            "gender",
            class_display
            ,
            concat_ws(
                '-',
                COALESCE("age_at_visit",''),
                COALESCE("doc_type_display",''),
                COALESCE("enc_class_code",''),
                COALESCE("gender",''),
                COALESCE(class_display,'')
                
            ) AS id
        FROM null_replacement
        GROUP BY
            cube(
            "age_at_visit",
            "doc_type_display",
            "enc_class_code",
            "gender",
            class_display
            
            )
    )

    SELECT
        s.cnt_documentreference_ref AS cnt,
        p."age_at_visit",
        p."doc_type_display",
        p."enc_class_code",
        p."gender",
        p.class_display
    FROM powerset AS p
    JOIN secondary_powerset AS s on s.id = p.id
    WHERE 
        p.cnt_subject_ref >= 10
        AND s.cnt_documentreference_ref >= 10
);