create or replace view irae__lab_creatinine_cystatin_c as select * from (values
('http://loinc.org', '33863-2', 'Cystatin C [Mass/volume] in Serum or Plasma')
,('http://loinc.org', '47612-7', 'Cystatin C [Mass/volume] in Urine')
,('http://loinc.org', '54380-1', 'Cystatin C [Mass/volume] in 24 hour Urine')
,('http://loinc.org', '54381-9', 'Cystatin C [Mass/time] in 24 hour Urine')
) AS t (system, code, display) ;