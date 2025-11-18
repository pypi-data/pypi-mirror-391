create or replace view irae__include_age_at_visit as 
select * from (values
(0,120)
) AS t (age_min,age_max) ;