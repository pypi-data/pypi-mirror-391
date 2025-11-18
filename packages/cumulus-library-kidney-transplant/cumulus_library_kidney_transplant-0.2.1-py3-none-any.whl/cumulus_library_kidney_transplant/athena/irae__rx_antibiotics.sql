create or replace view irae__rx_antibiotics as 
 select 'rx_antibiotics_any' as valueset, system, code, display from 
 irae__rx_antibiotics_any
 UNION ALL
select 'rx_antibiotics_systemic' as valueset, system, code, display from 
 irae__rx_antibiotics_systemic