create or replace view irae__dx_heart as 
 select 'dx_heart_attack' as valueset, system, code, display from 
 irae__dx_heart_attack
 UNION ALL
select 'dx_heart_cardiomyopathy' as valueset, system, code, display from 
 irae__dx_heart_cardiomyopathy
 UNION ALL
select 'dx_heart_cohort' as valueset, system, code, display from 
 irae__dx_heart_cohort
 UNION ALL
select 'dx_heart_failure' as valueset, system, code, display from 
 irae__dx_heart_failure