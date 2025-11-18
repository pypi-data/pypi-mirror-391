create or replace view irae__dx_immunocompromised as 
 select 'dx_immunocompromised_any' as valueset, system, code, display from 
 irae__dx_immunocompromised_any