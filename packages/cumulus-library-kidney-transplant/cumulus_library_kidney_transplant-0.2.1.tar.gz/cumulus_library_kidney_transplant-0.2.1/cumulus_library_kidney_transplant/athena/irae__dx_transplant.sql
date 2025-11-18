create or replace view irae__dx_transplant as 
 select 'dx_transplant_kidney' as valueset, system, code, display from 
 irae__dx_transplant_kidney
 UNION ALL
select 'dx_transplant_recipient' as valueset, system, code, display from 
 irae__dx_transplant_recipient
 UNION ALL
select 'dx_transplant_solid_organ' as valueset, system, code, display from 
 irae__dx_transplant_solid_organ
 UNION ALL
select 'dx_transplant_stem_cell' as valueset, system, code, display from 
 irae__dx_transplant_stem_cell