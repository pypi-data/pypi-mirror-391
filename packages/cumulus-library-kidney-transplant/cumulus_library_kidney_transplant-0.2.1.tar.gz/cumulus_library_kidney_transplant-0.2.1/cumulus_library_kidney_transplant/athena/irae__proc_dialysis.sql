create or replace view irae__proc_dialysis as 
 select 'proc_dialysis_services' as valueset, system, code, display from 
 irae__proc_dialysis_services