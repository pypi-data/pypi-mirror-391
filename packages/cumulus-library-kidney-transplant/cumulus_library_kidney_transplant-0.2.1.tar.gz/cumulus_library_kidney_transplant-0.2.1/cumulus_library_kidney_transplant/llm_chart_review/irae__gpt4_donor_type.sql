create or replace view irae__gpt4_donor_type as
WITH value_counts as (
	select subject_ref, donor_type, count(*) as cnt
	from irae__gpt4_parsed
	where  donor_type is NOT null and donor_type != 'NotMentioned' and donor_type != 'NA'
	group by subject_ref, donor_type
),
ranked_tf as (
	select subject_ref, donor_type, cnt,
	row_number() over ( partition by subject_ref order by cnt DESC, donor_type ASC) as rn
	from value_counts )
SELECT subject_ref, donor_type as donor_type_best, cnt from ranked_tf
where rn =1 order by subject_ref
