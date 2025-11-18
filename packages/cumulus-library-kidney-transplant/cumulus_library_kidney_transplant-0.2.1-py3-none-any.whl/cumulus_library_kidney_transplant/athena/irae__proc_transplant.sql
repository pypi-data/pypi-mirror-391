create or replace view irae__proc_transplant as 
 select 'proc_transplant_kidney' as valueset, system, code, display from 
 irae__proc_transplant_kidney
 UNION ALL
select 'proc_transplant_other_major' as valueset, system, code, display from 
 irae__proc_transplant_other_major
 UNION ALL
select 'proc_transplant_recipient' as valueset, system, code, display from 
 irae__proc_transplant_recipient
 UNION ALL
select 'proc_transplant_solid_organ' as valueset, system, code, display from 
 irae__proc_transplant_solid_organ
 UNION ALL
select 'proc_transplant_stem_cell' as valueset, system, code, display from 
 irae__proc_transplant_stem_cell