create or replace view irae__gpt4_donor_date as
WITH date_counts AS (
    SELECT
        subject_ref,
        donor_date,
        COUNT(*) AS cnt
    from    irae__gpt4_parsed
    where   donor_date is not null
    and     donor_date > date('2000-01-01')
    GROUP BY subject_ref, donor_date
),
ranked_dates AS (
    SELECT  cnt, subject_ref, donor_date,
        ROW_NUMBER() OVER (
            PARTITION BY subject_ref
            ORDER BY cnt DESC, donor_date ASC  -- break ties consistently
        ) AS rn
    FROM date_counts
)
SELECT      cnt, subject_ref,
            donor_date as donor_date_best
FROM        ranked_dates
WHERE       rn = 1
ORDER BY    subject_ref;