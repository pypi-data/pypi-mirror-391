create or replace view irae__rx_diuretics as 
 select 'rx_diuretics_loop' as valueset, system, code, display from 
 irae__rx_diuretics_loop
 UNION ALL
select 'rx_diuretics_potassium' as valueset, system, code, display from 
 irae__rx_diuretics_potassium
 UNION ALL
select 'rx_diuretics_thiazide' as valueset, system, code, display from 
 irae__rx_diuretics_thiazide