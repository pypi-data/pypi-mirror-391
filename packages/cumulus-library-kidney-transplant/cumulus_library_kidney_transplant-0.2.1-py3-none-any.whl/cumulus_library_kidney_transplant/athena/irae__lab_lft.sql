create or replace view irae__lab_lft as 
 select 'lab_lft_function' as valueset, system, code, display from 
 irae__lab_lft_function
 UNION ALL
select 'lab_lft_ggt' as valueset, system, code, display from 
 irae__lab_lft_ggt
 UNION ALL
select 'lab_lft_inr' as valueset, system, code, display from 
 irae__lab_lft_inr
 UNION ALL
select 'lab_lft_pt' as valueset, system, code, display from 
 irae__lab_lft_pt