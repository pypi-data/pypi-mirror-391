create or replace view irae__rx_htn as 
 select 'rx_htn_drugs' as valueset, system, code, display from 
 irae__rx_htn_drugs