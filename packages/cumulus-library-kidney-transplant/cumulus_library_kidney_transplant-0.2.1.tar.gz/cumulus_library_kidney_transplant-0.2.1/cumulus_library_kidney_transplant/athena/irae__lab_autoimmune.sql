create or replace view irae__lab_autoimmune as 
 select 'lab_autoimmune_blood_esr' as valueset, system, code, display from 
 irae__lab_autoimmune_blood_esr
 UNION ALL
select 'lab_autoimmune_crp' as valueset, system, code, display from 
 irae__lab_autoimmune_crp
 UNION ALL
select 'lab_autoimmune_serum_rf' as valueset, system, code, display from 
 irae__lab_autoimmune_serum_rf
 UNION ALL
select 'lab_autoimmune_t3' as valueset, system, code, display from 
 irae__lab_autoimmune_t3
 UNION ALL
select 'lab_autoimmune_t4' as valueset, system, code, display from 
 irae__lab_autoimmune_t4
 UNION ALL
select 'lab_autoimmune_tsh' as valueset, system, code, display from 
 irae__lab_autoimmune_tsh