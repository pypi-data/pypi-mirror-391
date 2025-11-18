create or replace view irae__rx_diabetes as 
 select 'rx_diabetes_drugs' as valueset, system, code, display from 
 irae__rx_diabetes_drugs