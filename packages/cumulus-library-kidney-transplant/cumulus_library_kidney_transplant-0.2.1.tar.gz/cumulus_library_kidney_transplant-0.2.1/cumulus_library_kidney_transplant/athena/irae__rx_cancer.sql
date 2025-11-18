create or replace view irae__rx_cancer as 
 select 'rx_cancer_ade_neutropenia' as valueset, system, code, display from 
 irae__rx_cancer_ade_neutropenia
 UNION ALL
select 'rx_cancer_checkpoint' as valueset, system, code, display from 
 irae__rx_cancer_checkpoint
 UNION ALL
select 'rx_cancer_chemo_advanced' as valueset, system, code, display from 
 irae__rx_cancer_chemo_advanced
 UNION ALL
select 'rx_cancer_keytruda' as valueset, system, code, display from 
 irae__rx_cancer_keytruda