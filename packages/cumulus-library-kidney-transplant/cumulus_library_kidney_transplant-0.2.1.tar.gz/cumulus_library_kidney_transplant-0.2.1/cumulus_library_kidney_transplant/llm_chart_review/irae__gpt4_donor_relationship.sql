create or replace view irae__gpt4_donor_relationship as
WITH value_counts as (
	select subject_ref, donor_relationship, count(*) as cnt
	from irae__gpt4_parsed
	where  donor_relationship is NOT null and donor_relationship != 'NotMentioned' and donor_relationship != 'NA'
	group by subject_ref, donor_relationship
),
ranked_tf as (
	select subject_ref, donor_relationship, cnt,
	row_number() over ( partition by subject_ref order by cnt DESC, donor_relationship ASC) as rn
	from value_counts )
SELECT subject_ref, donor_relationship as donor_relationship_best, cnt from ranked_tf
where rn =1 order by subject_ref
