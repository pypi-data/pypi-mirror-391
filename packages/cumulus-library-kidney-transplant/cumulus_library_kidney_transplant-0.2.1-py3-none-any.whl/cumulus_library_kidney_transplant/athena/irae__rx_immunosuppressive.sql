create or replace view irae__rx_immunosuppressive as 
 select 'rx_immunosuppressive_coricosteroids_systemic' as valueset, system, code, display from 
 irae__rx_immunosuppressive_coricosteroids_systemic
 UNION ALL
select 'rx_immunosuppressive_drugs' as valueset, system, code, display from 
 irae__rx_immunosuppressive_drugs
 UNION ALL
select 'rx_immunosuppressive_immune_modulators' as valueset, system, code, display from 
 irae__rx_immunosuppressive_immune_modulators
 UNION ALL
select 'rx_immunosuppressive_systemic_therapy' as valueset, system, code, display from 
 irae__rx_immunosuppressive_systemic_therapy