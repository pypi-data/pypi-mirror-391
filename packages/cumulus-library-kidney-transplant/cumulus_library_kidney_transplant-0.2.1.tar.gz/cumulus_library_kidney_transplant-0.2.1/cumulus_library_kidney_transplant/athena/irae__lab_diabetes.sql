create or replace view irae__lab_diabetes as 
 select 'lab_diabetes_glucose_test' as valueset, system, code, display from 
 irae__lab_diabetes_glucose_test
 UNION ALL
select 'lab_diabetes_screening' as valueset, system, code, display from 
 irae__lab_diabetes_screening