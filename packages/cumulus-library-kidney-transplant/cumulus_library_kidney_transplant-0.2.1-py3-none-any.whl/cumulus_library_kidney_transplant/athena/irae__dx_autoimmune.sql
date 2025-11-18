create or replace view irae__dx_autoimmune as 
 select 'dx_autoimmune_arthritis_ra' as valueset, system, code, display from 
 irae__dx_autoimmune_arthritis_ra
 UNION ALL
select 'dx_autoimmune_crohns' as valueset, system, code, display from 
 irae__dx_autoimmune_crohns
 UNION ALL
select 'dx_autoimmune_ibd' as valueset, system, code, display from 
 irae__dx_autoimmune_ibd
 UNION ALL
select 'dx_autoimmune_inflammatory' as valueset, system, code, display from 
 irae__dx_autoimmune_inflammatory
 UNION ALL
select 'dx_autoimmune_lupus' as valueset, system, code, display from 
 irae__dx_autoimmune_lupus