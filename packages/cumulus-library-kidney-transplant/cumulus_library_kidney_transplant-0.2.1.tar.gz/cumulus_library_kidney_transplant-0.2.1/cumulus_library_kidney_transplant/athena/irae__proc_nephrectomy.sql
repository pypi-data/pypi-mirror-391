create or replace view irae__proc_nephrectomy as 
 select 'proc_nephrectomy_icd10pcs' as valueset, system, code, display from 
 irae__proc_nephrectomy_icd10pcs
 UNION ALL
select 'proc_nephrectomy_sct' as valueset, system, code, display from 
 irae__proc_nephrectomy_sct